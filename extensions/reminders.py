from datetime import datetime, timezone

from discord.ext import commands
from humanize import precisedelta

import core
from core.bot import CustomBot
from core.context import CustomContext
from utils.time import parse_time


class Reminders(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    async def create_timer(self, ctx: CustomContext, content, expires: datetime, created: datetime=datetime.utcnow()):
        query = (
            """
            INSERT INTO
                reminders (guild, author, channel, message, expires, created, content)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """
        )
        values = (
            ctx.guild.id,
            ctx.author.id,
            ctx.channel.id,
            ctx.message.id,
            expires,
            created,
            content
        )
        await self.bot.pool.execute(query, *values)

        return True

    @core.command()
    async def remind(self, ctx: CustomContext, time: str, *, thing: str = "Nothing"):
        when = parse_time(ctx, time).replace(tzinfo=None)
        delta = precisedelta(when - datetime.utcnow())
        await self.create_timer(ctx, thing, when)

        await ctx.send(f"I'll remind you in {delta} to: {thing}")


def setup(bot):
    bot.add_cog(Reminders(bot))
