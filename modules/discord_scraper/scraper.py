from discord.ext import commands
from discord import File
from sys import maxsize as inf
from .stats import Inferer


class Scraper(Inferer, commands.Cog, name='Discord Scraping'):
    ''' Not usually available '''
    
    scrapping = False

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def scrapPics(self, ctx):
        """
            Loop through Every message in the current channel,
            compile a .txt of links to all (supported) images found
        """
        if self.scrapping:
            await ctx.send("Currently unavailable")
            return
        self.scrapping = True
        # TODO turn this into decorator

        await ctx.send("Job started")
        embedTypes = {}
        with open("picLinks.txt", "w+") as file1:
            file1.write("" +"\n")
            async for msg in ctx.channel.history(limit=inf):
                if not self.scrapping:
                    await ctx.send("Job cancelled")
                    return
                    
                for atch in msg.attachments:
                    file1.write(atch.url +"\n")
                for embed in msg.embeds:
                    try:
                        if embed.type == "rich":
                            if hasattr(embed, "image"):
                                file1.write(embed.image.url +"\n")
                        elif embed.type == "image":
                            file1.write(embed.url +"\n")
                        elif embed.type == "gifv":
                            file1.write(embed.url +"\n")

                        if hasattr(embedTypes, embed.type):
                            embedTypes[embed.type] += 1
                        else:
                            embedTypes[embed.type] = 1
                    except:
                        pass
        # print(embedTypes)
        await ctx.send(file=File("picLinks.txt"))
        self.scrapping = True

    @scrapPics.command(pass_context=False)
    async def stop(self, ctx):
        """Cancel current job"""
        self.scrapping = False
        await ctx.send("Freed")

def setup(bot):
    bot.add_cog(Scraper(bot))
