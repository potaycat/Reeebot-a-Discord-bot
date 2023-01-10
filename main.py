import os
import asyncio
import discord
from discord.ext.commands import Bot
from dotenv import load_dotenv
from modules.easter_egg import ee_lore_player, eeEV_recognize
from help_cmd import MyHelpCommand

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX")
LOGGING_CHANNEL_ID = int(os.getenv("LOGGING_CHANNEL_ID"))
OWNER_ID = int(os.getenv("BOT_OWNER"))

ee_lore = ee_lore_player.LorePlayerManager()
eeEV = eeEV_recognize.eeAware()


class Reeebot(Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=MyHelpCommand(),
            case_insensitive=True,
        )
        self.startup_extensions = [
            "modules.echo",
            "modules.RCE",
            "modules.web_scraper",
            "modules.image_manip",
            # "modules.image_awareness",
            "modules.text_generation",
        ]
        self.OWNER_ID = OWNER_ID
        self.PREFIX = PREFIX

    # def _skip_check(message.author.id, self.user.id): ...
    async def setup_hook(self):
        print(self.user.name, "is setting up...")
        for ext in self.startup_extensions:
            await self.load_extension(ext)
        c = await self.tree.sync(guild=None)
        print("Synced", c.__len__(), "commands")

    async def on_ready(self):
        self.log_channel = self.get_channel(LOGGING_CHANNEL_ID)
        await self.log_channel.send(f"Online {PREFIX}")
        print("READY")

    async def on_guild_join(self, guild):
        await self.log_channel.send(f"Joined {guild}")

    async def on_message(self, msg):
        try:
            if (c := msg.content).startswith(PREFIX) and len(c) > len(PREFIX):
                await ee_lore.replyIfMatch(msg)
            elif self.user.id in [m.id for m in msg.mentions]:
                await ee_lore.replyIfMatch(msg)
                await asyncio.gather(
                    msg.channel.send(
                        f"Hi <@{msg.author.id}>! Type `{PREFIX}help` to see my commands"
                    ),
                    eeEV.replyIfMatch(msg),
                )
        except Exception as e:
            await msg.channel.send(f"```{e}```")
        await self.process_commands(msg)

    async def on_command_error(self, ctx, error):
        await ctx.send(f"```{error}```")


if __name__ == "__main__":
    bot = Reeebot()
    bot.run(TOKEN)
