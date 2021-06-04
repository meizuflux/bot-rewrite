import asyncio

from discord.ext import commands


class CustomBot(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        loop = asyncio.get_event_loop()
        super().__init__(self, *args, **kwargs, loop=loop)
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()

        self.context = commands.Context

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or self.context)
