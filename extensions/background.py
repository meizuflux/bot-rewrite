import asyncio
from collections import defaultdict
from logging import getLogger

from discord.ext import commands, tasks

from core.bot import CustomBot
from core.context import CustomContext
from utils.decos import wait_until_prepped

log = getLogger(__name__)


class BackgroundEvents(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        self._lock = asyncio.Lock(loop=self.bot.loop)
        self._data = {
            "commands": []
        }

        self.bulk_command_insert.start()

    def cog_unload(self):
        self.bulk_command_insert.stop()

    @tasks.loop(seconds=10)
    @wait_until_prepped()
    async def bulk_command_insert(self):
        if self._data["commands"] is not []:
            total = len(self._data["commands"])
            async with self._lock:
                await self.bot.pool.command_insert(self._data["commands"])
                self._data["commands"].clear()
            log.info(f"Inserted {total} commands.")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: CustomContext):
        if ctx.command is None:
            return

        async with self._lock:
            self._data["commands"].append(
                {
                    "guild": getattr(ctx.guild, "id", None),
                    "channel": ctx.channel.id,
                    "author": ctx.author.id,
                    "used": ctx.message.created_at.isoformat(),
                    "prefix": ctx.clean_prefix,
                    "command": ctx.command.qualified_name,
                    "failed": ctx.command_failed
                }
            )






def setup(bot):
    bot.add_cog(BackgroundEvents(bot))
