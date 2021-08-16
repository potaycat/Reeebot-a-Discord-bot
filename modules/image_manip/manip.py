from discord.ext import commands
from discord import File
from .presets import ImageFilterer
from .color_quantizer import ColorQuantizer


class QuickImageEdit(commands.Cog, name='Image Manipulating'):
    """
        Perform image processing.
        Send along user mention, image link or image attachment.
        Leave blank for your own avatar.
    """

    @commands.command()
    async def deepfry(self, ctx):
        """
            Lmao
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
            UwU
        """
        img = ImageFilterer()
        url = img.image_url_from_msg(ctx.message)
        img.open_from_url(url)
        img.wholesome()
        file_path = img.export_png()
        await ctx.send(file=File(file_path))

    @commands.group(invoke_without_command=True)
    async def palette(self, ctx, limit=None):
        """
            Create a color palette from an image using color quantization methods.
            Usage: `palette <number of colors> <image url or leave blank>`
        """
        img = ColorQuantizer()
        url = img.image_url_from_msg(ctx.message)
        img.open_from_url(url)
        img.nearest_color_quantize(limit=limit)
        file_path = img.export_png()
        await ctx.send(file=File(file_path))

    @palette.command()
    async def kmeans(self, ctx, n_clusters=8):
        """
            Use k-means
            Usage: `kmeans <number of colors> <image url or leave blank>`
        """
        img = ColorQuantizer()
        url = img.image_url_from_msg(ctx.message)
        img.open_from_url(url)
        img.kmeans_quantize(n_clusters=n_clusters)
        file_path = img.export_png()
        await ctx.send(file=File(file_path))



def setup(bot):
    bot.add_cog(QuickImageEdit(bot))
