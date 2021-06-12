import sys

cog = sys.argv[1]
file = sys.argv[2]

script = f"""
from __future__ import annotations
from discord.ext import commands
import discord

import core
from core.bot import CustomBot
from core.context import CustomContext

class {cog}(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot
    
def setup(bot: CustomBot):
    bot.add_cog({cog}(bot))
"""

with open(f"./extensions/{file}.py", "w") as f:
    f.write(script)

print(f"Created cog at ./extensions/{file}.py")