from discord.ext import commands, tasks

from core.bot import CustomBot


class BackgroundEvents(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot


def setup(bot):
    bot.add_cog(BackgroundEvents(bot))
