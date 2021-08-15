from discord.ext import commands
import re


class Inferer():

    @commands.command()
    async def calFur(self, ctx, channel_name="general", limit_msg=15000):
        """
            A somewhat statistically, kinda accurate algorithm to calculate
            furriness level in #<channel_name>
        """
        if self.scrapping:
            await ctx.send("Currently unavailable")
            return
        self.scrapping = True

        attr_ls = ctx.__dir__()
        print(attr_ls)
        chnnl = None
        for channel in ctx.guild.channels:
            if channel_name == channel.name:
                chnnl = channel
                break
            if channel_name in channel.name:
                chnnl = channel
        if not hasattr(chnnl, 'history'):
            await ctx.send(f"Can't find \"#{channel_name}\" channel")
            return
        await ctx.send(f"*Absorbing <#{chnnl.id}>...*")
        
        fd = {'uwu': 0, 'owo': 0 , 'other': 0}
        frry_wrds = list(fd.keys())
        oldest = None
        async for msg in chnnl.history(limit=limit_msg):
            if not self.scrapping:
                await ctx.send("Job cancelled")
                return

            oldest = msg.created_at
            text = msg.content.lower()
            text = re.split(r'[\.\?!\n]', text)
            for sentence in text:
                if len(sentence) == 3:
                    if sentence in frry_wrds:
                        fd[sentence] += 1
                    else:
                        fd['other'] += 1

        # await ctx.send(fd)
        score = (fd['owo']*3+fd['uwu'])/(fd['other']+1) *500
        score = 100 if score>100 else score
        await ctx.send(f"<#{chnnl.id}> has released around **{round(score,2)}%** furry energy since {oldest.strftime('%d/%m/%Y')}")
        self.scrapping = False
        