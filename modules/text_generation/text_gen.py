from discord.ext import commands
from .backend import GPT2Wrapper
from .chatbot import Talking


class AITextGenerator(commands.Cog, name='Text Generator'):

    t_gen = GPT2Wrapper
    haunting = {}

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def crappost(self, ctx):
        """
            Generate with a model trained on pokedex entries
        """
        from_str = ctx.message.content.split(' ', 1)
        print(from_str)
        if len(from_str) > 1:
            from_str = from_str[1]
        else:
            from_str = ""
        print(from_str)
        text = self.t_gen.gen(from_str)
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
        if (cid:=ctx.channel.id) in self.haunting:
            await ctx.send("`Already registered`")
            return
        async with ctx.typing():
            self.haunting[cid] = Talking(ctx)
            await ctx.send(f"I'll talk in this channel!")
        await self.haunting[cid].run()

    @talkhere.command()
    async def fallfor(self, ctx, *mentions):
        if (cid:=ctx.channel.id) in self.haunting:
            await ctx.send(f'Fallen for {mentions} 😍')
            self.haunting[cid].pingable = mentions
        else:
            await ctx.send(f'`talkhere` first')

    @talkhere.command()
    async def instant(self, ctx):
        if (cid:=ctx.channel.id) in self.haunting:
            self.haunting[ctx.channel.id].running = False
        self.haunting[cid] = Talking(ctx, instant_mode=True)
        await ctx.send(f"I'm happy to talk to you")
        await self.haunting[cid].run()

    @talkhere.command()
    async def stoptalking(self, ctx):
        if (cid:=ctx.channel.id) in self.haunting:
            self.haunting[ctx.channel.id].running = False
            del self.haunting[cid]
            await ctx.send(f"I won't talk")
        else:
            await ctx.send(f"I'm not talking")



def setup(bot):
    GPT2Wrapper()
    bot.add_cog(AITextGenerator(bot))
