from discord.ext import commands
from utils import run_blocking, dict2embed
import os
import discord
from revChatGPT.Official import AsyncChatbot
import requests
import logging
import asyncio
from .backend import GPTWrapper
import json


class ChatCog(commands.Cog, name="5. I talk"):
    def __init__(self, bot):
        self.bot = bot
        self.LLM1 = "PygmalionAI/pygmalion-1.3b"
        self.USE_FILE = True

        self.cb = AsyncChatbot(os.getenv("OPENAI_API_KEY"))
        GPTWrapper(self.LLM1)
        if self.USE_FILE:
            self.DATA_PATH = "data/chatbot_hist"
            os.makedirs(self.DATA_PATH, exist_ok=True)
            self.chuser_dat = self.load_chat_data()
        else:
            self.chuser_dat = {}

        logging.basicConfig(level=logging.INFO, force=True)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("ChatCog init!")

    def load_chat_data(self):
        saved_data = {}
        for file in os.listdir(self.DATA_PATH):
            chnl_id, ext = file.split(".")
            if ext == "json":
                with open(os.path.join(self.DATA_PATH, file), "r") as f:
                    chnl_data = json.load(f)
                saved_data[int(chnl_id)] = chnl_data
        return saved_data

    def save_chat_data(self, chnl_id: int, data):
        self.chuser_dat[chnl_id] |= data
        if self.USE_FILE:
            with open(os.path.join(self.DATA_PATH, f"{chnl_id}.json"), "w") as f:
                json.dump(self.chuser_dat[chnl_id], f)

    def get_or_create_chat_data(self, chnl_id: int):
        data = self.chuser_dat.get(chnl_id)
        if not data:
            # Initialize save data
            data = {
                "history": [],
                "char_settings": {},
                "gen_settings": {},
            }
            self.chuser_dat[chnl_id] = data
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
            hook = await ctx.channel.create_webhook(name="Reon sonas")
            await ok()
            return hook
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
                reply = "> **" + f"{u_msg}** - <@{ctx.author.id}>\n{reply}"[-1996:]
                await hook_send(reply)
            else:
                reply = "> **" + f"{u_msg}**\n{reply}"[-1996:]
                await ctx.reply(reply)
        else:
            if hook:
                await hook_send(reply)
            else:
                await ctx.send(reply)

    @commands.hybrid_group(invoke_without_command=True, fallback="chit")
    async def chat(self, ctx, *, message, reset_chat=False):
        """
        Roleplay or something (pygmalion-1.3b)
        """
        webhook = self.preflight(ctx)
        chat_dat = self.get_or_create_chat_data(ctx.author.id)
        if reset_chat:
            chat_dat["history"] = []
        history = chat_dat["history"]
        reply = await run_blocking(
            (
                GPTWrapper.inference_fn,
                history,
                message,
                GPTWrapper.generation_settings | chat_dat["gen_settings"],
                GPTWrapper.char_settings | chat_dat["char_settings"],
            )
        )
        history.append(f"You: {message}")
        history.append(reply)

        async def monitor():
            log_instance = {
                "asker": f"{ctx.author} ({ctx.author.id})",
                "msg_url": "<" + ctx.message.jump_url + ">",
                "model": self.LLM1,
                "history": history[-2:],
                "char_settings": chat_dat["char_settings"],
                "gen_settings": chat_dat["gen_settings"],
                "revision": "230204",
            }
            self.logger.info(log_instance)
            await self.bot.low_log_channel.send(str(log_instance)[:2000])

        await asyncio.gather(
            self.reply(
                ctx,
                webhook,
                message,
                reply.replace("Reon:", "").replace("<USER>", ctx.author.name).strip(),
                {
                    "name": "Reon Cat Mode",
                    "avatar_url": "https://cdn.discordapp.com/attachments/759021098468638733/1071955114560077895/58501299_BFIxwff1D9QpslP.png",
                },
            ),
            run_blocking((self.save_chat_data, ctx.author.id, chat_dat)),
            monitor(),
        )

    @chat.command()
    async def chit_settings(
        self,
        ctx,
        reset=False,
        # gen
        do_sample: bool = None,
        max_new_tokens: int = None,
        temperature: float = None,
        top_p: float = None,
        top_k: int = None,
        typical_p: float = None,
        repetition_penalty: float = None,
        # chara
        char_name: str = None,
        char_persona: str = None,
        char_greeting: str = None,
        world_scenario: str = None,
        example_dialogue: str = None,
    ):
        """
        Your settings
        """
        chat_dat = self.get_or_create_chat_data(ctx.author.id)
        if reset:
            chat_dat["gen_settings"] = {}
            chat_dat["char_settings"] = {}

        if do_sample is not None:
            chat_dat["gen_settings"]["do_sample"] = do_sample
        if max_new_tokens is not None:
            chat_dat["gen_settings"]["max_new_tokens"] = max_new_tokens
        if temperature is not None:
            chat_dat["gen_settings"]["temperature"] = temperature
        if top_p is not None:
            chat_dat["gen_settings"]["top_p"] = top_p
        if top_k is not None:
            chat_dat["gen_settings"]["top_k"] = top_k
        if typical_p is not None:
            chat_dat["gen_settings"]["typical_p"] = typical_p
        if repetition_penalty is not None:
            chat_dat["gen_settings"]["repetition_penalty"] = repetition_penalty

        if char_name is not None:
            chat_dat["char_settings"]["char_name"] = char_name
        if char_persona is not None:
            chat_dat["char_settings"]["char_persona"] = char_persona
        if char_greeting is not None:
            chat_dat["char_settings"]["char_greeting"] = char_greeting
        if world_scenario is not None:
            chat_dat["char_settings"]["world_scenario"] = world_scenario
        if example_dialogue is not None:
            chat_dat["char_settings"]["example_dialogue"] = example_dialogue

        settings = {
            "history": chat_dat["history"][-3:],
            "gen_settings": GPTWrapper.generation_settings | chat_dat["gen_settings"],
            "char_settings": GPTWrapper.char_settings | chat_dat["char_settings"],
        }
        await ctx.interaction.response.send_message(
            f"```{json.dumps(settings, indent=2)}```", ephemeral=True
        )

    @chat.command()
    async def know_it_all(
        self,
        ctx,
        *,
        question,
        maid_mode=False,
        temperature: float = 0.5,
        reset_chat=False,
    ):
        """
        Answer questions, do code (text-davinci-002)
        """
        webhook = self.preflight(ctx)
        if reset_chat:
            self.cb.reset()
            return await ctx.reply("Reset chat ok")
        if maid_mode:
            prompt = "Talk in the style of a maid Umbreon. " + question
            sona = {
                "name": "Reon Maid Mode",
                "avatar_url": "https://cdn.discordapp.com/attachments/759021098468638733/1071955024336396348/e6b.jpg",
            }
        else:
            prompt = question
            sona = {
                "name": "Reon Assist Mode",
                "avatar_url": "https://cdn.discordapp.com/attachments/759021098468638733/1071955024336396348/e6b.jpg",
            }

        async def monitor(res=None):
            em = discord.Embed()
            em.set_author(
                name=f"{ctx.author}({ctx.author.id})", icon_url=ctx.author.avatar.url
            )
            em.add_field(name="Question", value=prompt[:200])
            em.add_field(name="Temperature", value=temperature)
            em.add_field(name="Meassage Url", value=ctx.message.jump_url)
            em.set_footer(text=f"Guild: {ctx.guild}")
            if res:
                em.add_field(name="Answer", value=res[:200])
            await self.bot.low_log_channel.send(embed=em)

        for i in range(3):
            try:
                res = await self.cb.ask(prompt, temperature, ctx.author.name)
                if not res:
                    raise Exception("Caught a hiccup.")
                break
            except Exception as e:
                self.logger.error(e)
                if i == 2:
                    await ctx.reply(f"```{e}```")
                    await monitor()
                    return
                await asyncio.sleep(3)
        await self.reply(
            ctx, webhook, question, (t := res["choices"][0]["text"].strip()), sona
        )
        await monitor(t)


async def setup(bot):
    await bot.add_cog(ChatCog(bot))
