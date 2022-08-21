from discord.ext import commands
import os

LOGGING_CHANNEL_ID = int(os.getenv("LOGGING_CHANNEL_ID"))


class RCE(commands.Cog, name="5. Expert Mode"):
    @commands.command()
    async def execute(self, ctx, *, snippet=""):
        """
        Executes python snippet.
        Works only in servers with the bot creator already a member.
        Activities are recorded.
        Execution time limited to 15 minutes each.
        """
        await self.get_channel(LOGGING_CHANNEL_ID).send(
            f"Executing snippet. Link: {ctx.message.jump_url}"
        )

        result = eval(snippet)
        await ctx.send(f"{result}")


async def setup(bot):
    await bot.add_cog(RCE(bot))
