from discord.ext import commands


class CommandMixin:
    def __init__(self, func, name, **attrs):
        super().__init__(func, name=name, **attrs)
        self.examples: tuple = attrs.pop("examples", (None,))


class Command(CommandMixin, commands.Command):
    pass


class Group(Command, commands.Group):
    pass


def command(name=None, cls=None, **attrs):
    if not cls:
        cls = Command

    def decorator(func):
        if isinstance(func, (Command, commands.Command)):
            raise TypeError('Callback is already a command.')
        return cls(func, name=name, **attrs)

    return decorator


def group(name=None, **attrs):
    attrs.setdefault('cls', Group)
    return command(name=name, **attrs)
