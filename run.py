import asyncio
import os
from asyncio import gather
from traceback import format_exception

import click
import discord
from asyncpg import create_pool

from core.bot import CustomBot
from core.config import postgres_uri, token


def run_bot():
    intents = discord.Intents.default()
    intents.members = True

    flags = discord.MemberCacheFlags.from_intents(intents)

    bot = CustomBot(
        skip_after_prefix=True,
        case_insensitive=True,
        intents=intents,
        member_cache_flags=flags,
        max_messages=750,
        owner_id=809587169520910346,
    )

    os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
    os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
    os.environ["JISHAKU_HIDE"] = "True"
    os.environ["PYTHONIOENCODING"] = "UTF-8"

    bot.run(token)


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        run_bot()


@main.group()
def db():
    pass


@db.command()
def init():
    run = asyncio.get_event_loop().run_until_complete
    try:
        pool = run(create_pool(dsn=postgres_uri))
    except Exception as err:
        tb = format_exception(type(err), err.__traceback__, err)
        click.echo(f"Could not create database connection.\n{tb}", err=True)
        return

    files = (
        "general.sql",
        "twitch.sql",
        "indexes.sql",
    )
    coros = []
    for file in files:
        with open("scripts/sql/" + file, encoding="utf8") as f:
            coros.append(pool.execute(f.read()))
    gather(coros)
