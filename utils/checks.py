from discord.ext import commands

__all__ = ("can_run",)

from core.context import CustomContext

can_run = commands.bot_has_permissions

has_permissions = commands.has_permissions
