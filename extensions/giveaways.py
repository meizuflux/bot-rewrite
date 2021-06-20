from discord.ext import commands

import core
from core.bot import CustomBot
from core.context import CustomContext

__all__ = ("setup",)

from utils.time import parse_time


class Giveaways(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.tada = "\uD83C\uDF89"

    @core.command(aliases=("gcreate", "giveawaycreate", "giveaway_create", "cgiveaway"))
    async def create_giveaway(self, ctx: CustomContext):
        timer = self.bot.get_cog("Reminders")
        expires = parse_time(ctx, "10 seconds")
        data = {"message": 12345678910, "prize": "Free Steam Key lol"}
        await timer.create_timer("giveaway", ctx.message.created_at, expires, data)

    @commands.Cog.listener()
    async def on_giveaway_complete(self, reminder):
        print(reminder)


def setup(bot: CustomBot):
    bot.add_cog(Giveaways(bot))
