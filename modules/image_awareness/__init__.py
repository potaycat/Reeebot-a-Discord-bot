from discord.ext import commands
from .backend import ImageStore, ClassPredictor


class ImageAware(commands.Cog, name="4. Image Awareness"):
    @commands.group(invoke_without_command=True)
    async def whichEV(self, ctx):
        """
        Tries to tell which Eeveelution is in an image or avatar
        Open source link: https://colab.research.google.com/drive/15mm41wCpEHrbsCSV3NR4xfEmYn0qmntp
        """
        img = ImageStore()
        await img.load_from_msg(ctx.message)
        argMaxLabel = ClassPredictor.most_likely(img.image_)
        await ctx.send(argMaxLabel)

    @whichEV.command()
    async def noArgmax(self, ctx):
        img = ImageStore()
        await img.load_from_msg(ctx.message)
        out_tensor = ClassPredictor.predict(img.image_)
        await ctx.send(f"{out_tensor}\n{ClassPredictor.labels}")


async def setup(bot):
    ClassPredictor()
    await bot.add_cog(ImageAware(bot))
