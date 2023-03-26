from discord.ext import commands
from discord.app_commands import choices, Choice
from utils import run_blocking, dict2embed, alt_thread
import os
import discord
import logging
import asyncio
import json
from .const import ChatSona, ChatConf
import openai


class ChatCog(commands.Cog, name="5. I talk"):
    def __init__(self, bot):
        self.bot = bot
        self.chat = openai.ChatCompletion
        self.chat_hist = {}
        self.chat_mode = {}
        self.chuser_dat = {}

    @alt_thread
    def save_chat_data(self, chnl_id: int, data):
        self.chuser_dat[chnl_id] |= data
        if ChatConf.USE_FILE:
            with open(os.path.join(ChatConf.DATA_PATH, f"{chnl_id}.json"), "w") as f:
                json.dump(self.chuser_dat[chnl_id], f)

    def get_or_create_chat_data(self, chnl_id: int):
        data = self.chuser_dat.get(chnl_id)
        if not data:
            # Initialize save data
            self.chuser_dat[chnl_id] = data = ChatConf.SAVE_DAT_STRUCT
        return data

    async def get_or_create_webhook(self, ctx):
        i = ctx.interaction

        async def ok():
            if i:
                await i.response.send_message("`Recieved`", ephemeral=True)

        try:
            for hook in await ctx.channel.webhooks():
                if hook.name == "Reon sonas":
                    await ok()
                    return hook
            await ok()  # respond here to avoid timeout
            return await ctx.channel.create_webhook(name="Reon sonas")
        except:
            if i:
                await i.response.defer()
            return None

    def preflight(self, ctx):
        # https://github.com/discordjs/discord.js/issues/5702
        return asyncio.create_task(self.get_or_create_webhook(ctx))

    async def reply(self, ctx, hook, u_msg, reply, sona=None):
        hook = await hook
        hook_send = lambda m: hook.send(
            m,
            username=sona["name"],
            avatar_url=sona["avatar_url"],
        )
        if ctx.interaction:
            if hook:
                reply = "> **" + f"{u_msg}** - <@{ctx.author.id}>\n\n{reply}"[-1996:]
                await hook_send(reply)
            else:
                reply = "> **" + f"{u_msg}**\n\n{reply}"[-1996:]
                await ctx.reply(reply)
        else:
            if hook:
                await hook_send(reply)
            else:
                await ctx.send(reply)

    async def monitor(self, ctx, q, mode, res):
        r_ = json.loads(str(res))
        r_["choices"][0]["message"]["content"] = r_["choices"][0]["message"]["content"][
            :200
        ]
        d_ = {
            "asker": f"{ctx.author} ({ctx.author.id})",
            "msg_url": "<" + ctx.message.jump_url + ">",
            "command": "hey reon " + mode,
            "revision": "230327",
            "question": q[:200],
            "response": str(r_),
        }
        await self.bot.low_log_channel.send(d_)

    @commands.hybrid_group(fallback="reon")
    @choices(
        mode=[
            Choice(name="Maid", value="maid"),
            Choice(name="Cat", value="cat"),
            Choice(name="Assistant", value="raw"),
            Choice(name="Yours (Coming soon)", value="yours"),
        ]
    )
    async def hey(self, ctx, *, message, mode: Choice[str] = None):
        """
        Talk about anything (gpt-3.5-turbo)
        """
        webhook = self.preflight(ctx)
        user_dat = self.get_or_create_chat_data(ctx.author.id)
        mode = user_dat["default_mode"] if mode == None else mode.value
        match mode:
            case "maid":
                sona = ChatSona.MAID
            case "cat":
                sona = ChatSona.CAT
            case "raw":
                sona = ChatSona.ASSIST
            case _:
                sona = ChatSona.FLUFFY
        if self.chat_mode.get(cid := ctx.channel.id) != mode:
            self.chat_mode[cid] = mode
            self.chat_hist[cid] = []
        hist = self.chat_hist.get(cid, [])[-3:]
        user_in = {"role": "user", "content": message}
        prompt = sona["starter"] + hist + [user_in]

        @alt_thread
        def ask():
            for i in range(3):
                try:
                    return self.chat.create(
                        model="gpt-3.5-turbo",
                        temperature=sona["temperature"],
                        messages=prompt,
                        max_tokens=sona["max_tokens"],
                    )
                except:
                    pass

        res = await ask()
        await self.reply(ctx, webhook, message, res.choices[0].message.content, sona)
        if res.usage.prompt_tokens < sona["max_tokens"]:
            hist.append(user_in)
        hist.append(res.choices[0].message)
        self.chat_hist[cid] = hist
        try:
            await self.monitor(ctx, message, mode, res)
        except Exception as e:
            await self.bot.low_log_channel.send(f"```{e}```<{ctx.message.jump_url}>")

    @commands.command()
    async def hey_(self, ctx, *, q=""):
        await self.hey(ctx, message=q)

    @commands.command()
    async def hey_maid(self, ctx, *, q=""):
        await self.hey(ctx, message=q, mode="maid")

    @commands.command()
    async def hey_cat(self, ctx, *, q=""):
        await self.hey(ctx, message=q, mode="cat")

    @commands.command()
    async def hey_assistant(self, ctx, *, q=""):
        await self.hey(ctx, message=q, mode="raw")

    @hey.command()
    @choices(
        default_mode=[
            Choice(name="Maid", value="maid"),
            Choice(name="Cat", value="cat"),
            Choice(name="Assistant", value="raw"),
            Choice(name="Fluffy", value="fluffy"),
        ]
    )
    async def reon_settings(
        self,
        ctx,
        reset=False,
        default_mode: Choice[str] = None,
        reset_all=False,
    ):
        """
        Your settings
        """
        uid = ctx.author.id
        if reset:
            self.chat_hist[ctx.channel.id] = []
            return await ctx.reply("Reset chat ok")
        if reset_all:
            self.chuser_dat.pop(uid, None)
            return await ctx.reply("Reset all ok")

        user_dat = self.get_or_create_chat_data(uid)
        if default_mode:
            user_dat["default_mode"] = default_mode.value

        await self.save_chat_data(uid, user_dat)
        if i := ctx.interaction:
            await i.response.send_message(user_dat, ephemeral=True)
        else:
            await ctx.send(user_dat)


async def setup(bot):
    await bot.add_cog(ChatCog(bot))
