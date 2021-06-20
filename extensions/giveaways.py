import discord
from discord.ext import commands

import core
from core.bot import CustomBot
from core.context import CustomContext

__all__ = ("setup",)


class Giveaways(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot


def setup(bot: CustomBot):
    bot.add_cog(Giveaways(bot))
