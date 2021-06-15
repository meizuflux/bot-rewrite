import sys

cog = sys.argv[1]
file = cog.lower()

script = f"""import discord
from discord.ext import commands

import core
from core.bot import CustomBot
from core.context import CustomContext

__all__ = ("setup",)


class {cog}(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot


def setup(bot: CustomBot):
    bot.add_cog({cog}(bot))
"""

with open(f"./extensions/{file}.py", "w") as f:
    f.write(script)

print(f"Created cog at ./extensions/{file}.py")
