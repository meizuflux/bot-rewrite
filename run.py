import os
import sys
from asyncio import get_event_loop
from traceback import format_exc

import click
import discord
from asyncpg import Pool, create_pool

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


@click.group(invoke_without_command=True, options_metavar="[options]")
@click.pass_context
def main(ctx):
    """Launches the bot."""
    if ctx.invoked_subcommand is None:
        run_bot()


@main.group(short_help="database stuff", options_metavar="[options]")
def db():
    pass


@db.command(short_help="initialises the databases for the bot", options_metavar="[options]")
@click.option("-s", "--show", help="show the output", is_flag=True)
@click.option("-r", "--run", help="run bot after", is_flag=True)
def init(show: bool, run: bool):
    run = get_event_loop().run_until_complete
    try:
        pool: Pool = run(create_pool(dsn=postgres_uri))
    except Exception as err:
        click.echo(f"Could not create database connection.\n{format_exc()}", err=True)
        return

    files = (
        "general.sql",
        "users.sql",
        "events.sql",
        "stats.sql",
        "indexes.sql",
    )
    for file in files:
        with open("scripts/sql/" + file, encoding="utf8") as f:
            read = f.read()
            if show:
                print(read)
            try:
                run(pool.execute(read))
            except Exception:
                click.echo(f"Failed on file {file}.\n{format_exc()}", err=True)

    click.echo("Created tables.", file=sys.stderr)

    if run:
        run_bot()


if __name__ == "__main__":
    main()
