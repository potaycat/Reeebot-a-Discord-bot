import os
import discord
from discord.ext.commands import Bot
from dotenv import load_dotenv
from help_cmd import MyHelpCommand
import logging

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX")
LOGGING_CHANNEL_ID = int(os.getenv("LOGGING_CHANNEL_ID"))
LOW_LOGGING_CHANNEL_ID = int(os.getenv("LOW_LOGGING_CHANNEL_ID"))
IMG_DUMP_CHANNEL_ID = int(os.getenv("IMG_DUMP_CHANNEL_ID"))
OWNER_ID = int(os.getenv("BOT_OWNER"))
DATA_PATH = "data/"


class Reeebot(Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(
            command_prefix=[PREFIX, PREFIX.title()],
            intents=intents,
            help_command=MyHelpCommand(),
            case_insensitive=True,
        )
        self.startup_extensions = [
            "modules.echo",
            "modules.RCE",
            "modules.web_scraper",
            "modules.image_manip",
            "modules.image_generation",
            "modules.text_generation",
        ]
        self.OWNER_ID = OWNER_ID
        self.PREFIX = PREFIX

    async def setup_hook(self):
        print(self.user.name, "is setting up...")
        for ext in self.startup_extensions:
            await self.load_extension(ext)
            print("Loaded:", ext)
        c = await self.tree.sync(guild=None)
        print("Synced", c.__len__(), "commands")

    async def on_ready(self):
        self.log_channel = self.get_channel(LOGGING_CHANNEL_ID)
        self.low_log_channel = self.get_channel(LOW_LOGGING_CHANNEL_ID)
        self.img_dump_chnl = self.get_channel(IMG_DUMP_CHANNEL_ID)
        print("READY")

    async def on_guild_join(self, guild):
        await self.log_channel.send(f"Joined {guild}")

    async def on_command_error(self, ctx, error):
        await ctx.send(f"```{error}```")
        await self.low_log_channel.send(f"```{error}``` {ctx.message.jump_url}")


if __name__ == "__main__":
    os.makedirs(DATA_PATH, exist_ok=True)
    logging.basicConfig(
        # filename=os.path.join(DATA_PATH, "reeebot.log"),
        level=logging.INFO,
    )
    bot = Reeebot()
    bot.run(TOKEN)
