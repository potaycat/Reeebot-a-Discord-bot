import os
import asyncio
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
from modules.easter_egg import ee_lore_player, eeEV_recognize
from help_cmd import MyHelpCommand

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX")
LOGGING_CHANNEL_ID = int(os.getenv("LOGGING_CHANNEL_ID"))

intents = Intents.default()
intents.members = True
intents.message_content = True
startup_extensions = [
    "modules.echo",
    "modules.RCE",
    "modules.web_scraper",
    "modules.image_manip",
    # "modules.image_awareness",
    # "modules.text_generation",
]
ee_lore = ee_lore_player.LorePlayerManager()
eeEV = eeEV_recognize.eeAware()

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=MyHelpCommand(),
    case_insensitive=True,
)

# bot._skip_check(message.author.id, self.user.id)

@bot.event
async def on_ready():
    print(bot.user.name, "has connected to Discord!")
    await bot.get_channel(LOGGING_CHANNEL_ID).send("Online " + PREFIX)


@bot.event
async def on_message(msg):
    try:
        if (c := msg.content).startswith(PREFIX) and len(c) > len(PREFIX):
            await ee_lore.replyIfMatch(msg)
        elif bot.user.id in [m.id for m in msg.mentions]:
            await ee_lore.replyIfMatch(msg)
            await asyncio.gather(
                msg.channel.send(
                    f"Hi <@{msg.author.id}>! Type `{PREFIX}help` to see my commands"
                ),
                eeEV.replyIfMatch(msg),
            )
    except Exception as e:
        await msg.channel.send(f"```{e}```")
    await bot.process_commands(msg)


@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"```{error}```")


@bot.hybrid_command(name="ping")
async def cal_ping(ctx):
    await ctx.send(f"Pong! Latency: {bot.latency}")


async def main():
    for extension in startup_extensions:
        await bot.load_extension(extension)
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
