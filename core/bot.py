import logging
from asyncio import AbstractEventLoop, Event
from random import SystemRandom
from typing import List, Union

import discord
from aiohttp import ClientSession
from discord.ext import commands

from core import config
from utils.db import CustomPool, create_pool

log = logging.getLogger("bot")
logging.basicConfig(level=logging.INFO)


def get_prefix(bot: "CustomBot", message: discord.Message) -> Union[List[str], str]:
    return commands.when_mentioned_or(*config.prefix)(bot, message)


class CustomBot(commands.Bot):
    loop: AbstractEventLoop

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._BotBase__cogs = commands.core._CaseInsensitiveDict()

        self.pool: CustomPool = self.loop.run_until_complete(
            create_pool(bot=self, dsn=config.postgres_uri, loop=self.loop)
        )
        self.loop.create_task(self.__prep())
        self.prepped = Event()

        self.random = SystemRandom()

        self.context = commands.Context

    async def __prep(self):
        self.session = ClientSession(
            headers={"User-Agent": "Walrus (https://github.com/ppotatoo/bot-rewrite)"}
        )
        with open("schema.sql") as f:
            await self.pool.execute(f.read())
        await self.wait_until_ready()
        async with self.pool.acquire() as conn:
            await conn.executemany(
                "INSERT INTO guilds (id) VALUES ($1) ON CONFLICT DO NOTHING",
                tuple((g.id,) for g in self.guilds),
            )
        self.prepped.set()

    def load_extensions(self):
        extensions = [
            "jishaku",
            "core.context",
            "extensions.help" "extensions.osu",
            "extensions.errorhandler",
            "extensions.interactions",
            "extensions.reminders",
        ]
        for ext in extensions:
            self.load_extension(ext)
        log.info("Loaded extensions")

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or self.context)

    def run(self, *args, **kwargs):
        self.load_extensions()
        super().run(*args, **kwargs)

    async def on_ready(self):
        log.info("Connected to Discord.")

    @staticmethod
    def embed(**kwargs):
        color = kwargs.pop("color", discord.Color.blurple())
        return discord.Embed(**kwargs, color=color)

    async def paste(self, data: str, url="https://mystb.in"):
        async with self.session.post(url + "/documents", data=bytes(str(data), "utf-8")) as r:
            res = await r.json()
        key = res["key"]
        return url + f"/{key}"
