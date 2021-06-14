from typing import List, Mapping, Union

import discord
from discord import ui
from discord.ext import commands

import core
from core.context import CustomContext

__all__ = ("setup",)


class CustomHelp(commands.HelpCommand):
    context: CustomContext

    async def filter_commands(self, cmds, *, sort=True, key=None):
        if sort and key is None:
            key = lambda c: c.name

        iterator = cmds if self.show_hidden else list(filter(lambda c: not c.hidden, cmds))

        return sorted(iterator, key=key) if sort else iterator

    def get_sig(self, command):
        sig = command.signature
        if not sig and not command.parent:
            return f"`{self.context.clean_prefix}{command.name}`"
        if not command.parent:
            return f"`{self.context.clean_prefix}{command.name}` `{sig}`"
        if not sig:
            return f"`{self.context.clean_prefix}{command.parent}` `{command.name}`"
        return f"`{self.context.clean_prefix}{command.parent}` `{command.name}` `{sig}`"

    async def send(self, **send_kwargs):
        if not send_kwargs.get("view"):
            view = ui.View()
            view.add_item(
                ui.Button(
                    label="Invite Me", url="https://google.com", style=discord.ButtonStyle.grey
                )
            )
            view.add_item(
                ui.Button(
                    label="Join the Support Server", url="https://google.com", style=discord.ButtonStyle.grey
                )
            )

            send_kwargs["view"] = view

        destination = self.get_destination()
        await destination.send(**send_kwargs)

    async def send_bot_help(
        self, mapping: Mapping[commands.Cog, List[Union[core.Command, commands.Command]]]
    ):
        cogs = [
            f"{cog.emoji} `{self.context.clean_prefix}help` `{cog.qualified_name}`"
            for cog in mapping
            if hasattr(cog, "emoji")
        ]
        description = (
            "`<argument>` means the argument is required",
            "`[argument]` means the argument is optional\n",
            f"Send `{self.context.clean_prefix}help` `[command]` for more info on a command.",
            f"You can also send `{self.context.clean_prefix}help` `[module]` for more info on a particular module.",
        )
        embed = self.context.bot.embed(title=f"Bot Help", description="\n".join(description))
        embed.add_field(name="Modules", value="\n".join(cogs))
        await self.send(embed=embed)

    async def send_cog_help(self, cog: commands.Cog):
        if not hasattr(cog, "emoji") and not await self.context.bot.is_owner(self.context.author):
            return await self.send_error_message(self.command_not_found(cog.qualified_name))

        if getattr(cog, "show_subcommands", False) is True:
            _commands = list(cog.walk_commands())
        else:
            _commands = cog.get_commands()

        filtered = await self.filter_commands(_commands)
        _fmt = [self.get_sig(command) + f" " for command in filtered]
        embed = self.context.bot.embed(
            title=f"{cog.emoji} {cog.qualified_name}", description="\n".join(_fmt)
        )

        await self.send(embed=embed)

    async def send_command_help(self, command: Union[core.Command, commands.Command]):
        if not hasattr(command.cog, "emoji") and not await self.context.bot.is_owner(
            self.context.author
        ):
            return await self.send_error_message(self.command_not_found(command.qualified_name))

        ctx = self.context
        embed = ctx.bot.embed(
            title=f"{command.cog.qualified_name.lower()}:{command.qualified_name}"
        )
        help_string = command.help or "No help was provided for this command ._."
        embed.description = help_string.format(prefix=ctx.clean_prefix)

        usage = self.get_sig(command)
        if returns := getattr(command, "returns", None):
            usage += "\nReturns: " + returns

        embed.add_field(name="Usage", value=usage, inline=False)

        if aliases := command.aliases:
            embed.add_field(name="Aliases", value="`" + "`, `".join(aliases) + "`", inline=True)

        if isinstance(command, core.Command):
            params = command.params_
            if isinstance(params, dict):
                _formatted = "\n".join(f"`{param}`: {value}" for param, value in params.items())
            else:
                _formatted = params

            embed.add_field(name="Parameters", value=_formatted)

            embed.add_field(
                name="Examples",
                value="\n".join(
                    f"`{ctx.clean_prefix}{command.qualified_name}` `{example}`"
                    if example
                    else f"`{ctx.clean_prefix}{command.qualified_name}`"
                    for example in command.examples
                ),
            )

        await self.send(embed=embed)


def setup(bot):
    bot.help_command = CustomHelp()


def teardown(bot):
    bot.help_command = commands.DefaultHelpCommand()
