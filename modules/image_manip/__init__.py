from discord.ext import commands
from discord import File, Attachment, User
from typing import Optional
from .presets import ImageFilterer
from .color_quantizer import ColorQuantizer


class QuickImageEdit(commands.Cog, name="3. Image Manipulating"):
    """
    Perform image processing.
    Send along user mention, image link or image upload.
    Leave blank for your own avatar.
    """

    @commands.hybrid_command()
    async def deepfry(
        self, ctx, avatar: Optional[User], upload: Optional[Attachment], img_link=""
    ):
        """
        Lmao an image
        """
        img = ImageFilterer()
        await img.load_from_msg(ctx.message, avatar, upload or img_link)
        img.deepfry()
        file_path = await img.export_png(
            f"{ctx.message.author}{ctx.message.created_at.timestamp()}"
        )
        await ctx.send(file=File(file_path))

    @commands.hybrid_command()
    async def wholesome(
        self, ctx, avatar: Optional[User], upload: Optional[Attachment], img_link=""
    ):
        """
        UwU
        """
        img = ImageFilterer()
        await img.load_from_msg(ctx.message, avatar, upload or img_link)
        img.wholesome()
        file_path = await img.export_png(
            f"{ctx.message.author}{ctx.message.created_at.timestamp()}"
        )
        await ctx.send(file=File(file_path))

    @commands.hybrid_group(invoke_without_command=True, fallback="colorful")
    async def palette(
        self,
        ctx,
        limit: Optional[int],
        avatar: Optional[User],
        upload: Optional[Attachment],
        img_link="",
    ):
        """
        Creates a color palette from an image.
        Pick between 2 color quantize methods.
        Usage: `palette <number of colors> <image url>`
        """
        img = ColorQuantizer()
        await img.load_from_msg(ctx.message, avatar, upload or img_link)
        img.nearest_color_quantize(limit=limit)
        file_path = img.export_png()
        await ctx.send(file=File(file_path))

    # @palette.command()
    async def kmeans(
        self,
        ctx,
        n_clusters: Optional[int] = 8,
        avatar: Optional[User] = None,
        upload: Optional[Attachment] = None,
        img_link="",
    ):
        """
        Uses k-means
        Usage: `palette kmeans <number of colors> <image url>`
        """
        img = ColorQuantizer()
        await img.load_from_msg(ctx.message, avatar, upload or img_link)
        img.kmeans_quantize(n_clusters=n_clusters)
        file_path = img.export_png()
        await ctx.send(file=File(file_path))


async def setup(bot):
    await bot.add_cog(QuickImageEdit(bot))
