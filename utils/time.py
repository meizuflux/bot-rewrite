import re
from core.context import CustomContext
from discord.ext import commands
from dateutil.relativedelta import relativedelta

TIME_REGEX = re.compile(
    """(?:(?P<years>[0-9])(?:years?|y))?             # e.g. 2y
                             (?:(?P<months>[0-9]{1,2})(?:months?|mo))?     # e.g. 2months
                             (?:(?P<weeks>[0-9]{1,4})(?:weeks?|w))?        # e.g. 10w
                             (?:(?P<days>[0-9]{1,5})(?:days?|d))?          # e.g. 14d
                             (?:(?P<hours>[0-9]{1,5})(?:hours?|h))?        # e.g. 12h
                             (?:(?P<minutes>[0-9]{1,5})(?:minutes?|m))?    # e.g. 10m
                             (?:(?P<seconds>[0-9]{1,5})(?:seconds?|s))?    # e.g. 15s
                          """,
    re.VERBOSE,
)


def parse_time(ctx: CustomContext, time: str):
    argument = time.replace(" ", "")
    match = TIME_REGEX.match(argument)
    if match is None or not match.group(0):
        raise commands.BadArgument("Invalid time provided.")
    data = {k: int(v) for k, v in match.groupdict(default=0).items()}
    return ctx.message.created_at + relativedelta(**data)
