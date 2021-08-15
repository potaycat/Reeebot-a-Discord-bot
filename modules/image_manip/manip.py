from discord.ext import commands
from discord import File
from .presets import ImageFilterer


class QuickImageEdit(commands.Cog, name='Image Manipulating'):
    """
        Danken images
    """

    @commands.command()
    async def deepfry(self, ctx):
        """
            Deep fries an image or avatar
            Usage: `deepfry <user mention or image link> or image attachment`
        """
        img = ImageFilterer()
        url = img.image_url_from_msg(ctx.message)
        img.open_from_url(url)
        img.deepfry()
        file_path = img.export_png()
        await ctx.send(file=File(file_path))

    @commands.command()
    async def wholesome(self, ctx):
        """
            Wholesomes an image or avatar
            Usage: `wholesome <user mention or image link> or image attachment`
        """
        img = ImageFilterer()
        url = img.image_url_from_msg(ctx.message)
        img.open_from_url(url)
        img.wholesome()
        file_path = img.export_png()
        await ctx.send(file=File(file_path))


def setup(bot):
    bot.add_cog(QuickImageEdit(bot))
