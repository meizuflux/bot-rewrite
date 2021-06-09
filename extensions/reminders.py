import discord
from discord.ext import commands

import core
from core.bot import CustomBot
from core.context import CustomContext
from utils.time import parse_time
from humanize import precisedelta


class Reminders(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    @core.command()
    async def remind(self, ctx: CustomContext, time: str, *, thing: str = "Nothing"):
        when = parse_time(ctx, time)
        await ctx.send(f"I'll remind you in {when.isoformat()} for: {thing}")

def setup(bot):
    bot.add_cog(Reminders(bot))
