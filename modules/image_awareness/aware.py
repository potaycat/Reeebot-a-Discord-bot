from discord.ext import commands
from .backend import ImageStore, ClassPredictor


class ImageAware(commands.Cog, name='Image Awareness'):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def whichEV(self, ctx):
        """
            Tells which Eeveelution is in an image or avatar (works best when face not obscured)
            Open source link: https://colab.research.google.com/drive/15mm41wCpEHrbsCSV3NR4xfEmYn0qmntp
        """
        img = ImageStore()
        url = img.image_url_from_msg(ctx.message)
        img.open_from_url(url)
        argMaxLabel = ClassPredictor.most_likely(img.get_img())
        await ctx.send(argMaxLabel)

    @whichEV.command()
    async def noArgmax(self, ctx):
        img = ImageStore()
        url = img.image_url_from_msg(ctx.message)
        img.open_from_url(url)
        out_tensor = ClassPredictor.predict(img.get_img())
        await ctx.send(f'{out_tensor}\n{ClassPredictor.labels}')



def setup(bot):
    ClassPredictor()
    bot.add_cog(ImageAware(bot))
