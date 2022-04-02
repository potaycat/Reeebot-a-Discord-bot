from discord.ext import commands


class RCE(commands.Cog, name='5. Expert Mode'):
    @commands.command()
    async def execute(self, ctx, *, snippet=""):
        """
            Execute python snippet
            Time limited to 5 minutes
        """
        result = eval(snippet)
        await ctx.send(f'{result}')


def setup(bot):
    bot.add_cog(RCE(bot))
