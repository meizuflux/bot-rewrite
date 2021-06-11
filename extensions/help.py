from discord.ext import commands


def setup(bot):
    bot.help_command = commands.DefaultHelpCommand()


def teardown(bot):
    bot.help_command = commands.DefaultHelpCommand()
