from typing import Counter
from discord.ext import commands
import discord

from utils import codeblock

import core
from core.bot import CustomBot
from core.context import CustomContext


__all__ = ("setup",)


class General(commands.Cog):
    """
    General commands, about the bot etc
    """

    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.emoji = "<a:pop_cat:854027957878390784>"

    async def send_socket_stats(self, ctx, stats, *, omit_minutes: bool = False) -> None:
        minutes = (discord.utils.utcnow() - self.bot.start_time).total_seconds() / 60
        total = 0
        lines = []

        for name, count in stats:
            total += count
            if not omit_minutes:
                lines.append(f"{name:<30}{count:<18}{round(count / minutes)} / minute\n")
            else:
                lines.append(f"{name:<30}{count:<18}\n")

        if not omit_minutes:
            msg = f"{''.join(lines)}\n{'TOTAL':<30}{total:<18}{round(total / minutes)} / minute"
        else:
            msg = f"{''.join(lines)}\n{'TOTAL':<30}{total:<18}"

        await ctx.send(codeblock(msg, lang="yaml"))

    @core.group(
        aliases=("socketstats", "socket_stats", "events"),
        returns="A chart showing socket stats of this bot.",
        invoke_without_command=True,
    )
    async def socket(self, ctx: CustomContext):
        await self.send_socket_stats(ctx, self.bot.extra.socket_stats.most_common())

    @socket.command(
        name="total", aliases=("all",), returns="A table showing the total socket stats"
    )
    async def socket_total(self, ctx: CustomContext):
        raw = await self.bot.pool.fetch("SELECT name, count FROM socket ORDER BY count DESC")
        stats = [(i["name"], i["count"]) for i in raw]
        await self.send_socket_stats(ctx, stats, omit_minutes=True)


def setup(bot: CustomBot):
    bot.add_cog(General(bot))
