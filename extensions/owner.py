import asyncio
import contextlib
import inspect
import io
import textwrap
import traceback

import asyncpg
import discord
import import_expression
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter
from jishaku.paginators import PaginatorInterface, WrappedPaginator
from tabulate import tabulate

import core
from core.bot import CustomBot
from core.context import CustomContext
from utils import codeblock
from utils.time import Timer

__all__ = ("setup",)


async def send(ctx: CustomContext, result, stdout_):
    try:
        await ctx.message.add_reaction("<:prettythumbsup:806390638044119050>")
    except (discord.HTTPException, discord.Forbidden):
        pass
    else:
        value = stdout_.getvalue()
        if not result:
            if value:
                await ctx.send(f"```py\n{value}\n```")
            return

        kwargs = {}

        if isinstance(result, discord.Embed):
            kwargs["embed"] = result
        elif isinstance(result, discord.File):
            kwargs["file"] = result

        if not isinstance(result, str):
            result = str(repr(result))

        if result.strip() == "":
            result = "\u200b"

        to_be_sent = f"{value}{result}".replace(ctx.bot.http.token, "< adios token >")

        if len(to_be_sent) < 1990:
            return await ctx.send(to_be_sent, **kwargs)

        paginator = WrappedPaginator(prefix="", suffix="", max_size=1990, wrap_on=("",))
        paginator.add_line(to_be_sent)
        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        await interface.send_to(ctx)


class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.pool = self.bot.pool

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @core.command()
    async def eval(self, ctx: CustomContext, *, argument: codeblock_converter):
        env = {
            "ctx": ctx,
            "discord": discord,
            "commands": commands,
            "bot": ctx.bot,
            "channel": ctx.channel,
            "guild": ctx.guild,
            "message": ctx.message,
            "reference": ctx.message.reference,
            "find": discord.utils.find,
            "get": discord.utils.get,
            "core": core,
            "inspect": inspect,
            "asyncio": asyncio,
            "session": self.bot.session,
        }

        env.update(globals())

        code = textwrap.indent(argument.content, "    ")
        to_compile = f"async def execute():\n{code}"

        try:
            import_expression.exec(to_compile, env, locals())
        except Exception as err:
            return await ctx.send(f"```py\n" f"{err.__class__.__name__}: {err}```")

        func = locals()["execute"]
        with io.StringIO() as stdout:
            try:
                with contextlib.redirect_stdout(stdout):
                    to_exec = func()

                    if inspect.isasyncgenfunction(func):
                        async for output in to_exec:
                            if not output:
                                continue
                            await send(ctx, output, stdout)
                        return

                    result = await to_exec
                    await send(ctx, result, stdout)
            except Exception as err:
                base = (type(err), err, err.__traceback__)
                exception = "".join(traceback.format_exception(*base, limit=2))
                value = stdout.getvalue()
                return await ctx.send(f"```py\n{value}{exception}```"[:1990])

    @core.group()
    async def sql(self, ctx: CustomContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(ctx.command)

    @sql.command(aliases=("e",))
    async def execute(self, ctx: CustomContext, *, query: str):
        with Timer() as timer:
            ret = await self.pool.execute(query.strip("`"))
        await ctx.send(f"`{ret}`\n**Executed in {timer.ms}ms**")

    @sql.command(aliases=("f",))
    async def fetch(self, ctx: CustomContext, *, query: str):
        with Timer() as timer:
            ret = await self.pool.fetch(query.strip("`"))
        table = tabulate((dict(row) for row in ret), headers="keys", tablefmt="github")
        if len(table) > 1000:
            table = await self.bot.paste(table)
        await ctx.send(f"{codeblock(table)}\n**Retrieved {len(ret)} rows in {timer.ms:.2f}ms**")

    @sql.command(aliases=("fv",))
    async def fetchval(self, ctx: CustomContext, *, query: str):
        with Timer() as timer:
            ret = await self.pool.fetchval(query.strip("`"))
        await ctx.send(f"{codeblock(f'{ret!r}')}\n**Retrieved in {timer.ms}ms**")

    @sql.error
    async def sql_error(self, ctx: CustomContext, error: Exception):
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
            if isinstance(error, asyncpg.exceptions.PostgresSyntaxError):
                return await ctx.send(
                    embed=self.bot.embed(description=f"Syntax error:```\n {error} ```")
                )
        await ctx.send(error)

    @fetch.error
    async def fetch_error(self, ctx, error):
        await self.sql_error(ctx, error)

    @fetchval.error
    async def fetchval_error(self, ctx, error):
        await self.sql_error(ctx, error)

    @execute.error
    async def execute_error(self, ctx, error):
        await self.sql_error(ctx, error)


def setup(bot: CustomBot):
    bot.add_cog(Owner(bot))
