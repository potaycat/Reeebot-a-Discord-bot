from discord.ext import commands


class Echo(commands.Cog, name="1. Echoing"):
    """
    Text repeater
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="echo")
    async def ping(self, ctx, *, words=""):
        if words:
            await ctx.send(words)
        else:
            await ctx.send(f"Echo! Latency: {self.bot.latency}")

    @commands.hybrid_command()
    async def eeveefy(self, ctx, word):
        """
        Eeveefies a word
        """
        word = word.split(" ", 1)[0]
        response = word + ("e" if word[-1] != "e" else "") + "on"
        await ctx.send(response)


async def setup(bot):
    await bot.add_cog(Echo(bot))
