from discord.ext import commands
import random


class RNG(commands.Cog):

    @commands.command()
    async def randomev(self, ctx):
        """Returns a random eeveelution"""
        eevees = [
            "Eevee",
            "Vaporeon",
            "Jolteon",
            "Flareon",
            "Espeon",
            "Umbreon",
            "Leafeon",
            "Glaceon",
            "Sylveon",
        ]
        response = random.choice(eevees)
        await ctx.send(response)


def setup(bot):
    bot.add_cog(RNG(bot))
