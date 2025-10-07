from discord.ext import commands
from .pixiv import PixivApiUtilizer


class Scraper(commands.Cog, name="2. Web Scraping"):
    @commands.hybrid_command()
    async def pixiv(self, ctx, *, keywords):
        """
        Searches Pixiv for illustrations
        Usage: `pixiv <keywords>`
        """
        response = await PixivApiUtilizer.getSearchRes(keywords, ctx.channel.is_nsfw())
        await ctx.send(response)


async def setup(bot):
    await bot.add_cog(Scraper())
