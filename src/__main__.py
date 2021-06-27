import asyncio
import os
import logging
from asyncio import get_event_loop
from contextlib import suppress
from traceback import format_exc

import click
import uvicorn
from asyncpg import Pool, create_pool

from db import db
from web import app
from bot.core import CustomBot
from config import postgres_uri, token


log = logging.getLogger("runner")

async def run_bot(bot):
    bot.load_extensions()
    try:
        await bot.start(token)
    finally:
        if not bot.is_closed():
            await bot.close()

async def run_server(server: uvicorn.Server):
    try:
        await server.serve()
    finally:
        await server.shutdown()

async def run():
    os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
    os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
    os.environ["JISHAKU_HIDE"] = "True"
    os.environ["PYTHONIOENCODING"] = "UTF-8"

    
    bot = CustomBot()
    bot.pool = await db.create_pool(bot=bot, dsn=postgres_uri, loop=bot.loop)

    config = uvicorn.Config(app, use_colors=False, log_config=None, host="localhost")
    server = uvicorn.Server(config)
    server.install_signal_handlers = lambda *args, **kwargs: None

    await asyncio.gather(run_bot(bot), run_server(server))


@click.group(invoke_without_command=True, options_metavar="[options]")
@click.pass_context
def main(ctx):
    """Launches the bot."""
    if ctx.invoked_subcommand is None:
        asyncio.run(run())


@main.command(short_help="initialises the databases for the bot", options_metavar="[options]")
@click.option("-s", "--show", help="show the output", is_flag=True)
@click.option("-r", "--run", help="run bot after", is_flag=True)
def init(show: bool, run: bool):
    _run = get_event_loop().run_until_complete
    try:
        pool: Pool = _run(create_pool(dsn=postgres_uri))
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
        with open("src/scripts/sql/" + file, encoding="utf8") as f:
            read = f.read()
            if show:
                print(read)
            try:
                _run(pool.execute(read))
            except Exception:
                click.echo(f"Failed on file {file}.\n{format_exc()}", err=True)
                return

    log.info("Created tables.")

    if run:
        run_bot()


if __name__ == "__main__":
    try:
        import uvloop
    except ModuleNotFoundError:
        log.warning("uvloop is not installed")
    else:
        uvloop.install()
    try:
        main()
    except KeyboardInterrupt:
        pass
