from modules.easter_egg import ee_lore_player, eeEV_recognize
from discord import Intents
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX")
LOGGING_CHANNEL_ID = int(os.getenv("LOGGING_CHANNEL_ID"))

intents = Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, case_insensitive=True)
startup_extensions = [
    "modules.echo",
    "modules.RCE",
    "modules.web_scraper.scraper",
    "modules.image_manip.manip",
    "modules.image_awareness.aware",
    # "modules.text_generation.text_gen",
]


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")
    await bot.get_channel(LOGGING_CHANNEL_ID).send("Online " + PREFIX)


ee = ee_lore_player.LorePlayerManager()
eeEV = eeEV_recognize.eeAware()


@bot.event
async def on_message(msg):
    if (c := msg.content).startswith(PREFIX) and len(c) > 2:
        await ee.replyIfMatch(msg)
    elif c == "<@!758176006171000833>" or c == "<@758176006171000833>":
        await ee.replyIfMatch(msg)
        if matchThenReply := eeEV.recognize(msg.author.avatar_url):
            async with msg.channel.typing():
                await msg.channel.send(
                    f"{matchThenReply}Type `{PREFIX}help` to see my commands"
                )
        else:
            await msg.channel.send(
                f"Hi <@{msg.author.id}>! Type `{PREFIX}help` to see my commands"
            )
    await bot.process_commands(msg)


@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"```{error}```")


@bot.command(name="ping")
async def cal_ping(ctx):
    await ctx.send(f"Pong! Latency: {bot.latency}")


async def main():
    for extension in startup_extensions:
        await bot.load_extension(extension)
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
