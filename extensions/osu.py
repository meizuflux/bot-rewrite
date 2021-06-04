from discord.ext import commands

from core.bot import CustomBot


class Osu(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    async def acquire_bearer_token(self):
        while not self.bot.is_closed():
            pass


def setup(bot):
    bot.add_cog(Osu(bot))
