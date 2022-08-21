from discord.ext import commands
from .backend import GPT2Wrapper
from .chatbot import Talking


class AITextGenerator(commands.Cog, name="Text Synthesis"):

    haunting = {}

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def crappost(self, ctx):
        """
        Generate with a model trained on pokedex entries
        """
        from_str = ctx.message.content.split(" ", 1)
        if len(from_str) > 1:
            from_str = from_str[1]
        else:
            from_str = ""
        text = GPT2Wrapper.gen("crappost", from_str)
        await ctx.send(text)

    @commands.group(invoke_without_command=True)
    async def talkhere(self, ctx):
        """
        Reebot will occasionally talk in the channel.
        Current convo starter model: .
        Current replier model: Eh.
        Reply within 1200sec to start talking with it.
        Reply within 200sec to keep the convo going
        """
        if (cid := ctx.channel.id) in self.haunting:
            await ctx.send("`Already registered`")
            return
        async with ctx.typing():
            self.haunting[cid] = Talking(ctx)
            await ctx.send(f"I'll talk in this channel!")
        await self.haunting[cid].run()


async def setup(bot):
    GPT2Wrapper()
    await bot.add_cog(AITextGenerator(bot))
