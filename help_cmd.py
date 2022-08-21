import discord
from discord.ext import commands


class MyHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.paginator.prefix = "```python"