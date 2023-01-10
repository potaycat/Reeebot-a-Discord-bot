from discord.ext import commands
from .backend import GPT2Wrapper
from utils import arun_blocking
import os

from discord import Attachment
import pickle
import requests


def newRevChat(url=None):
    if url:
        r = requests.get(url, allow_redirects=True)
        cb = pickle.loads(r.content)
    else:
        with open("data/chatbot.pickle", "rb") as f:
            cb = pickle.load(f)
    return cb


class ChatCog(commands.Cog, name="5. I talk"):
    def __init__(self, bot):
        self.bot = bot
        self.cb = newRevChat()

    @commands.hybrid_command()
    async def chat(
        self,
        ctx,
        *,
        prompt,
        reset_chat=False,
        print_id=False,
        convo_id=None,
        parent_id=None,
    ):
        """
        ChatGPT
        """
        if reset_chat:
            self.cb.reset_chat()
            return await ctx.reply("Reset chat ok")
        if interrac := ctx.interaction:
            await interrac.response.defer()
            prepend = "> " + prompt
        else:
            prepend = ""
        # prompt = "Assistant roleplays as a Maid Umbreon. " + prompt
        try:
            print("ASKING...")
            res = await arun_blocking((self.cb.ask, prompt, convo_id, parent_id))
        except Exception as e:
            await ctx.reply("`Not available. I might be back in 1 minute or few hours`")
            await self.bot.get_user(self.bot.OWNER_ID).send(
                f"```{e}```\n{ctx.message.jump_url}"
            )
            return
        to_send = f"{prepend}\n{res['message']}"
        if print_id:
            to_send += (
                f"\n`convo_id:{res['conversation_id']} parent_id:{res['parent_id']}`"
            )
        await ctx.reply(to_send)
        print("ok")


async def setup(bot):
    # GPT2Wrapper()
    await bot.add_cog(ChatCog(bot))
