import asyncio
from collections import Counter, deque
from json import dumps
from logging import getLogger

import discord
from discord.ext import commands, tasks

from core.bot import CustomBot
from core.context import CustomContext
from utils.decos import wait_until_prepped

__all__ = ("setup",)

log = getLogger(__name__)



class BackgroundEvents(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        self._lock = asyncio.Lock(loop=self.bot.loop)

        self._commands = []
        self.message_latencies = deque(maxlen=500)
        self._socket_cache = Counter()

        self.bulk_command_insert.start()
        self.bulk_socket_insert.start()

    def cog_unload(self):
        self.bulk_command_insert.stop()
        self.bulk_socket_insert.stop()

    @tasks.loop(seconds=10)
    @wait_until_prepped()
    async def bulk_command_insert(self):
        if self._commands:
            total = len(self._commands)
            async with self._lock:
                await self.bot.pool.command_insert(dumps(self._commands))
                self._commands.clear()
            log.info(f"Inserted {total} commands.")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: CustomContext):
        if ctx.command is None:
            return

        async with self._lock:
            self._commands.append(
                {
                    "guild": getattr(ctx.guild, "id", None),
                    "channel": ctx.channel.id,
                    "author": ctx.author.id,
                    "used": ctx.message.created_at.isoformat(),
                    "prefix": ctx.clean_prefix,
                    "command": ctx.command.qualified_name,
                    "failed": ctx.command_failed,
                }
            )

    @tasks.loop(seconds=15)
    @wait_until_prepped()
    async def bulk_socket_insert(self):
        if self._socket_cache:
            async with self._lock:
                items = [(name, count) for name, count in self._socket_cache.most_common()]
                query = """
                    INSERT INTO 
                        socket
                    VALUES ($1, $2)
                    ON CONFLICT (name)
                    DO UPDATE SET 
                        count = socket.count + $2
                    """
                await self.bot.pool.executemany(query, items)
                self._socket_cache.clear()

    @commands.Cog.listener()
    async def on_socket_response(self, data):
        self.bot.extra.socket_stats["TOTAL"] += 1
        if event := data.get("t"):
            self.bot.extra.socket_stats[event] += 1

            self._socket_cache[event] += 1


def setup(bot):
    bot.add_cog(BackgroundEvents(bot))
