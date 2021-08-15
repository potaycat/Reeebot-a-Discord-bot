
from discord.ext import commands
from .pixiv import PixivApiUtilizer


class Scraper(commands.Cog, name='Web Scraping'):

    @commands.command()
    async def pixiv(self, ctx, keywords):
        """
            Searches Pixiv for illustrations
            Usage: `pixiv <keywords>`
        """
        response = PixivApiUtilizer.getSearchRes(
            ctx.message.content.split('pixiv ', 1)[1],
            ctx.channel.is_nsfw()
        )
        await ctx.send(response)


def setup(bot):
    bot.add_cog(Scraper(bot))
