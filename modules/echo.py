from discord.ext import commands
from .text_generation.backend import GPT2Wrapper


class Echo(commands.Cog, name="1. Echoing"):
    """
    Let the bot do something with your text
    """

    @commands.command()
    async def say(self, ctx, to_repeat=""):
        """
        Repeats something
        """
        if to_repeat == "":
            if GPT2Wrapper.initialized:
                await ctx.send(GPT2Wrapper.gen())
            else:
                await ctx.send("Hello")
        else:
            await ctx.send(ctx.message.content.split("say ", 1)[1])

    @commands.command()
    async def eeveefy(self, ctx, word="Eevee"):
        """
        Eeveefies a word
        """
        # if echo[-1] in ['a', 'e', 'i', 'o', 'u']:
        response = word.split(" ", 1)[0] + ("e" if word[-1] != "e" else "") + "on"
        await ctx.send(response)


async def setup(bot):
    await bot.add_cog(Echo(bot))
