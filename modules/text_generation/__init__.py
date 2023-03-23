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

        if ChatConf.USE_FILE:
            ChatConf.DATA_PATH = "data/chatbot"
            os.makedirs(ChatConf.DATA_PATH, exist_ok=True)
            self.chuser_dat = self.load_chat_data()
        else:
            self.chuser_dat = {}
        logging.basicConfig(level=logging.INFO, force=True)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("ChatCog init!")

    def load_chat_data(self):
        saved_data = {}
        for file in os.listdir(ChatConf.DATA_PATH):
            chnl_id, ext = file.split(".")
            if ext == "json":
                with open(os.path.join(ChatConf.DATA_PATH, file), "r") as f:
                    chnl_data = json.load(f)
                saved_data[int(chnl_id)] = chnl_data | ChatConf.SAVE_DAT_STRUCT
        return saved_data

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

    async def monitor(self, log_instance):
        self.logger.info(log_instance)
        await self.bot.low_log_channel.send(str(log_instance)[:2000])

    @commands.hybrid_group(fallback="reon")
    @choices(
        mode=[
            Choice(name="Maid", value="maid"),
            Choice(name="Cat", value="cat"),
            Choice(name="Assistant", value="raw"),
            Choice(name="Yours (Coming soon)", value="yours"),
        ]
    )
    async def hey(self, ctx, *, message, mode: Choice[str] = "fluffy"):
        """
        Talk about anything (gpt-3.5-turbo)
        """
        webhook = self.preflight(ctx)
        mode = str(mode)
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
        temperature = sona["temperature"]

        @alt_thread
        def ask():
            return self.chat.create(
                model="gpt-3.5-turbo",
                temperature=temperature,
                messages=prompt,
                max_tokens=2500,
            )

        res = await ask()
        if res.usage.prompt_tokens < 500:
            hist.append(user_in)
        if res.usage.completion_tokens < 500:
            hist.append(res.choices[0].message)
        self.chat_hist[cid] = hist
        await self.reply(ctx, webhook, message, res.choices[0].message.content, sona)

        async def monitor():
            r_ = json.loads(str(res))
            r_["choices"][0]["message"]["content"] = r_["choices"][0]["message"][
                "content"
            ][:200]
            d_ = {
                "asker": f"{ctx.author} ({ctx.author.id})",
                "msg_url": "<" + ctx.message.jump_url + ">",
                '"mode"': str(mode),
                "revision": "230324",
                "question": message[:200],
                "response": str(r_),
            }
            await self.bot.low_log_channel.send(d_)

        try:
            await monitor()
        except:
            pass

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
    async def reon_settings(
        self,
        ctx,
        reset=False,
        # temperature: float = None,
    ):
        """
        Your settings
        """
        chat_dat = self.get_or_create_chat_data(ctx.author.id)
        if reset:
            self.chat_hist[ctx.channel.id] = []
            await ctx.reply("Reset chat ok")
        else:
            await ctx.reply("More settings coming soon")


async def setup(bot):
    await bot.add_cog(ChatCog(bot))
