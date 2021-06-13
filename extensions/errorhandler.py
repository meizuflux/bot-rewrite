import asyncio
from traceback import format_exception

import discord
from discord.ext import commands

from core.bot import CustomBot
from core.context import CustomContext

__all__ = ("setup",)


class ErrorHandler(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: CustomContext, error: Exception):
        owner_errors = (
            commands.MissingAnyRole,
            commands.MissingPermissions,
            commands.MissingRole,
            commands.CommandOnCooldown,
            commands.DisabledCommand,
        )
        if await self.bot.is_owner(ctx.author) and isinstance(error, owner_errors):
            return await ctx.reinvoke()
        if ctx.command and ctx.command.has_error_handler():
            return
        if ctx.cog and ctx.cog.has_error_handler():
            return

        error = getattr(error, "original", error)

        if ctx.command and not isinstance(error, commands.CommandOnCooldown):
            ctx.command.reset_cooldown(ctx)

        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(
                    embed=self.bot.embed(
                        description=f"{ctx.invoked_with} can only be used in servers."
                    )
                )
            except discord.HTTPException:
                pass

        if isinstance(error, commands.MissingRequiredArgument):
            errors = str(error).split(" ", maxsplit=1)
            return await ctx.send(
                embed=self.bot.embed(
                    description=(
                        f"`{errors[0]}` {errors[1]}\n"
                        f"You can view the help for this command with `{ctx.clean_prefix}help` `{ctx.invoked_with}`"
                    )
                )
            )

        if isinstance(error, commands.DisabledCommand):
            return await ctx.send(
                embed=self.bot.embed(description=f"`{ctx.invoked_with}` has been disabled.")
            )

        if isinstance(error, commands.BadArgument):
            return await ctx.send(embed=self.bot.embed(title=str(error)))

        if isinstance(error, asyncio.TimeoutError):
            return await ctx.send(
                embed=self.bot.embed(description=f"{ctx.invoked_with} timed out.")
            )

        traceback = "".join(format_exception(type(error), error, error.__traceback__))
        if len(traceback) > 1000:
            traceback = await self.bot.paste(traceback)
        else:
            traceback = "```py\n" + traceback + "```"
        await ctx.send("Oops, an error occured. Here's some info on it: \n" + traceback)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
