from discord.ext import commands
from discord.app_commands import choices, Choice
from discord import File, Attachment, User
from typing import Optional
from .presets import ImageFilterer
from .color_quantizer import ColorQuantizer
from .presets_api import remove_bg


class QuickImageEdit(commands.Cog, name="3. Image Manipulating"):
    """
    Perform image processing.
    Send along user mention, image link or image upload.
    Leave blank for your own avatar.
    """

    @commands.hybrid_group(invoke_without_command=True, fallback="deepfry")
    async def quick(
        self, ctx, avatar: Optional[User], upload: Optional[Attachment], img_link=""
    ):
        """
        Lmao an image
        """
        x = ImageFilterer()
        await x.load_from_msg(ctx.message, avatar, upload or img_link)
        await x.deepfry()
        x = await x.export_png(
            f"{ctx.message.author}{ctx.message.created_at.timestamp()}"
        )
        await ctx.send(file=File(x))

    @quick.command()
    async def wholesome(
        self, ctx, avatar: Optional[User], upload: Optional[Attachment], img_link=""
    ):
        """
        UwU
        """
        x = ImageFilterer()
        await x.load_from_msg(ctx.message, avatar, upload or img_link)
        await x.wholesome()
        x = await x.export_png(
            f"{ctx.message.author}{ctx.message.created_at.timestamp()}"
        )
        await ctx.send(file=File(x))

    @quick.command()
    async def remove_background(
        self, ctx, avatar: Optional[User], upload: Optional[Attachment], img_link=""
    ):
        """
        Remove background
        """
        out_p = await remove_bg(ctx.message, avatar, upload or img_link)
        await ctx.send(file=File(out_p))

    @commands.hybrid_command()
    @choices(
        mode=[
            Choice(name="Colorful", value="colorful"),
            Choice(name="K-Means", value="kmeans"),
        ]
    )
    async def palette(
        self,
        ctx,
        avatar: Optional[User],
        upload: Optional[Attachment],
        img_link: Optional[str],
        mode: Choice[str] = None,
        limit: Optional[int] = 8,
    ):
        """
        Creates a color palette from an image.
        Usage: `palette <number of colors> <image url>`
        """
        x = ColorQuantizer()
        await x.load_from_msg(ctx.message, avatar, upload or img_link)
        if mode and mode.value == "kmeans":
            return await ctx.send("kmeans not available now")
            x.kmeans_quantize(n_clusters=limit)
        else:
            x.nearest_color_quantize(limit=limit)
        x = x.export_png()
        await ctx.send(file=File(x))

    # @commands.hybrid_command()
    # async def editor(
    #     self, ctx, avatar: Optional[User], upload: Optional[Attachment], img_link=""
    # ):


async def setup(bot):
    await bot.add_cog(QuickImageEdit(bot))
