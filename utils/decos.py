import functools

import discord
from discord.ext import commands

__all__ = ("wait_until_prepped", "wait_until_ready")


def event(func):
    def check(method):
        method.callback = method

        @functools.wraps(method)
        async def wrapper(*args, **kwargs):
            if await discord.utils.maybe_coroutine(func, *args, **kwargs):
                await method(*args, **kwargs)

        return wrapper

    return check


def wait_until_ready(bot=None):
    async def predicate(*args, **_):
        self = args[0] if args else None
        if isinstance(self, commands.Cog):
            _bot = bot or self.bot
        if not isinstance(_bot, commands.Bot):
            raise Exception(f"bot must derived from commands.Bot not {bot.__class__.__name__}")
        await _bot.wait_until_ready()
        return True

    return event(predicate)


def wait_until_prepped(bot=None):
    async def predicate(*args, **_):
        self = args[0] if args else None
        if isinstance(self, commands.Cog):
            _bot = bot or self.bot
        await _bot.prepped.wait()
        return True

    return event(predicate)
