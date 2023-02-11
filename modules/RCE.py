from discord.ext import commands
import discord
import os
import asyncio
import sys
import io
from contextlib import redirect_stdout


PREFIX = os.getenv("PREFIX")


def format_result(r):
    if r.__len__() > 1900:
        r = r[-1900:] + "\n`result trimmed to 1900 chars`"
    return r or "`Finished`"


class RCE(commands.Cog, name="4. Pythonista"):
    def __init__(self, bot):
        self.bot = bot
        self.TIME_OUT = 600

    def preprocess(self, s):
        if s.startswith(p := f"{PREFIX}run"):
            s = s[p.__len__() :].strip()
        if s.startswith("```"):
            s = s[3:-3]
        if s.startswith("python\n"):
            s = s[7:]
        return s

    @commands.command()
    async def run(self, ctx):
        """
        Executes python snippet.
        Works only in servers with the BOT_OWNER already a member.
        Activities are recorded.
        `bot`, `ctx` and `interaction` provided in `locals()`.
        Execution timeout: 10 minutes.
        """
        ok = False
        for mem in ctx.channel.members:
            if mem.id == self.bot.OWNER_ID:
                ok = True
                break
        if not ok:
            await ctx.send("BOT_OWNER not in channel")
            return

        _run = lambda i: self._run(ctx, i)
        result = await _run(None)
        rerun = Buttons(_run)
        try:
            rerun.res_msg = await ctx.reply(format_result(result), view=rerun)
        except:
            pass

    async def _run(self, ctx, interaction=None):
        snippet = self.preprocess(ctx.message.content)
        if not snippet:
            snippet = """print('Try `print("Hello world")`. \
You can edit the code then click "Rerun" to fix error.')"""

        async def execute_snippet():
            # https://stackoverflow.com/questions/44859165/async-exec-in-python
            # TODO solve blocking code
            exec(
                "async def __ex(ctx, bot, interaction):"
                + "\n def input(): raise Exception('input() not supported.')"
                + "".join(f"\n {l}" for l in snippet.split("\n"))
            )
            with io.StringIO() as buf, redirect_stdout(buf):
                await locals()["__ex"](ctx, self.bot, interaction)
                output = buf.getvalue()
            return output

        async def monitor():
            runner = ctx.message.author
            edited = True
            if interaction:
                runner = interaction.user
                if e := ctx.message.edited_at:
                    if (r := interaction.message.edited_at) and e < r:
                        edited = False
                else:
                    edited = False
            if runner.id == self.bot.OWNER_ID:
                return
            embed = discord.Embed(
                title="Running snippet [jump]", url=ctx.message.jump_url, color=0xFFA500
            )
            embed.add_field(name="Guild", value=ctx.guild)
            embed.add_field(name="Runner", value=runner)
            if edited:
                embed.add_field(
                    name="Snippet preview",
                    value="```python\n" + snippet[:1500] + "```",
                    inline=False,
                )
            await self.bot.log_channel.send(embed=embed)

        try:
            asyncio.create_task(monitor())
            result = await asyncio.wait_for(execute_snippet(), timeout=self.TIME_OUT)
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            result = f"```fix\n{exc_type.__name__}: {exc_obj}```"  # at line {exc_tb.tb_lineno}```"
        finally:
            return result


class Buttons(discord.ui.View):
    def __init__(self, _run):
        super().__init__(timeout=3600)
        self.execute = _run
        self.count = 1

    @discord.ui.button(
        label="Rerun",
        style=discord.ButtonStyle.gray,
    )
    async def retry(self, interaction, button):
        result = await self.execute(interaction)
        await interaction.response.edit_message(
            content=f"{format_result(result)}<@{interaction.user.id}>` reran ({self.count})`"
        )
        self.count += 1

    async def on_timeout(self):
        self.children[0].disabled = True
        await self.res_msg.edit(view=self)


async def setup(bot):
    await bot.add_cog(RCE(bot))
