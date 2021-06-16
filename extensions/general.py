from dataclasses import dataclass
from pathlib import Path

from discord.ext import commands
import discord

import core
from core.context import CustomContext
from core.bot import CustomBot
from utils import codeblock

__all__ = ("setup",)

@dataclass
class LineCounter:
    files: int
    lines: int
    characters: int
    classes: int
    functions: int
    coroutines: int
    comments: int

    @classmethod
    def project(cls, path="./"):
        files = lines = characters = classes = functions = coroutines = comments = 0
        for f in Path(path):
            if str(f).startswith("venv"):
                continue
            files += 1
            with open(f, 'w') as of:
                _lines = of.readlines()
                lines += len(_lines)
                for line in _lines:
                    line = line.strip()
                    characters += len(line)
                    if line.startswith("class"):
                        classes += 1
                    if line.startswith("def"):
                        functions += 1
                    if line.startswith("async def"):
                        coroutines += 1
                    if "#" in line:
                        comments += 1

        return cls(

        )



class General(commands.Cog):
    """General commands, about the bot etc"""

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

    @socket.command(name="total", aliases=("all",), returns="A table showing the total socket stats")
    async def socket_total(self, ctx: CustomContext):
        raw = await self.bot.pool.fetch("SELECT name, count FROM socket ORDER BY count DESC")
        stats = [(i["name"], i["count"]) for i in raw]
        await self.send_socket_stats(ctx, stats, omit_minutes=True)

    @core.command(returns="Things about the bot.")
    async def about(self, ctx: CustomContext):
        embed = self.bot.embed(color=discord.Color.og_blurple())

        me = await self.bot.getch_user(self.bot.owner_id)
        await ctx.send(me)
        embed.set_author(name=str(me))

        guilds = users = bots = text = voice = 0
        for guild in self.bot.guilds:
            guilds += 1
            if guild.unavailable is True:
                continue

            for user in guild.members:
                if user.bot is True:
                    bots += 1
                else:
                    users += 1

            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    text += 1
                if isinstance(channel, discord.VoiceChannel):
                    voice += 1

        query = """
            SELECT COUNT(*) FROM commands  
            """
        cmds = await self.bot.pool.fetchval(query)
        since_restart = sum(self.bot.extra.command_stats.values())

        fields = (
            ("Users", f"{users + bots} total\n{users} humands\n{bots} robots", False),
            ("Channels", f"{text + voice} total\n{text} text\n{voice} voice", False),
            ("Guilds", f"{guilds}", False),
            ("Command Usage", f"{cmds} total\n{since_restart} since restart", False),
        )

        for title, desc, inline in fields:
            embed.add_field(name=title, value=desc, inline=inline)

        await ctx.send(embed=embed)


def setup(bot: CustomBot):
    bot.add_cog(General(bot))
