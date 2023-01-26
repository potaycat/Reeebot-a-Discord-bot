from discord.ext import commands
from utils import run_blocking, dict2embed
import os
from discord import Attachment
import pickle
import requests
import logging
import asyncio


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
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command()
    async def chat(
        self,
        ctx,
        *,
        prompt,
        maid_mode=False,
        print_id=False,
        convo_id=None,
        parent_id=None,
        reset_chat=False,
    ):
        """
        ChatGPT proxy (experimental)
        """
        if interrac := ctx.interaction:
            await interrac.response.defer()
            prepend = "> " + prompt
        else:
            prepend = ""
        if reset_chat:
            self.cb.reset_chat()
            return await ctx.reply("Reset chat ok")
        if maid_mode:
            prompt = "Talk in the style of a maid Umbreon. " + prompt
        log_instance = {
            "asker": f"{ctx.author} ({ctx.author.id})",
            "question": prompt,
            "in_guild": str(ctx.guild),
            "msg_url": "<" + ctx.message.jump_url + ">",
        }
        self.logger.info(log_instance)
        log_instance=discord.Embed()
        log_instance.set_author(name=f"{ctx.author}({ctx.author.id})", icon_url=ctx.author.avatar.url)
        log_instance.add_field(name="Question", value=prompt)
        log_instance.add_field(name="Meassage Url", value=ctx.message.jump_url, inline=False)
        log_instance.set_footer(text=f"Guild: {ctx.guild}")
        for i in range(3):
            try:
                print("ASKING...")
                res = await run_blocking((self.cb.ask, prompt, convo_id, parent_id))
                if not res:
                    raise Exception("Caught a hiccup.")
                break
            except Exception as e:
                self.logger.error(e)
                if i == 2:
                    return await ctx.reply(f"```I have requests limit. {e}```")
                await asyncio.sleep(3)

        to_send = f"{prepend}\n{res['message']}"
        if print_id:
            to_send += (
                f"\n`convo_id:{res['conversation_id']} parent_id:{res['parent_id']}`"
            )
        await asyncio.gather(
            ctx.reply(to_send), self.bot.low_log_channel.send(embed=log_instance)
        )
        print("ok")


async def setup(bot):
    # GPT2Wrapper()
    await bot.add_cog(ChatCog(bot))
