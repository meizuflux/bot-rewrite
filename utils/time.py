import re
import time
from datetime import datetime as dt, timezone

from dateutil.relativedelta import relativedelta
from discord.ext import commands
from discord.utils import utcnow

from core.context import CustomContext
from .formats import human_join, plural

__all__ = ("parse_time", "human_timedelta", "Timer")

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


def parse_time(ctx: CustomContext, arg: str):
    argument = arg.replace(" and ", "").replace(" ", "")
    match = TIME_REGEX.match(argument)
    parsed = convert_date(argument)
    if parsed is None and (match is not None or match.group(0)):
        print("here?")
        data = {k: int(v) for k, v in match.groupdict(default=0).items()}
        parsed = ctx.message.created_at + relativedelta(**data)
    if parsed is None:
        raise commands.BadArgument("Could not discern a date from your input.")
    if utcnow() > parsed:
        raise commands.BadArgument("Time must be in the future, sorry.")

    return parsed.replace(tzinfo=timezone.utc)


# from rapptz
def human_timedelta(_dt, *, source=None, accuracy=3, suffix=True):
    now = source or _dt.utcnow()
    # Microsecond free zone
    now = now.replace(microsecond=0)
    _dt = _dt.replace(microsecond=0)

    if _dt > now:
        delta = relativedelta(_dt, now)
        suffix = ""
    else:
        delta = relativedelta(now, _dt)
        suffix = " ago" if suffix else ""

    attrs = [
        "year",
        "month",
        "day",
        "hour",
        "minute",
        "second",
    ]

    output = []
    for attr in attrs:
        elem = getattr(delta, attr + "s")
        if not elem:
            continue

        if attr == "day":
            weeks = delta.weeks
            if weeks:
                elem -= weeks * 7
                output.append(plural(f"{elem} week(s)", elem))

        if elem <= 0:
            continue

        output.append(plural(f"{elem} {attr}(s)", elem))

    if accuracy is not None:
        output = output[:accuracy]

    if len(output) == 0:
        return "now"
    else:
        return str(human_join(output, final="and")) + suffix


class Timer:
    def __init__(self):
        self._start = None
        self._end = None

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self._end = time.perf_counter()
        self.elapsed = self._end - self._start
        self.ms = self.elapsed * 1000

    def __int__(self):
        return round(self.elapsed)

    def __float__(self):
        return self.elapsed

    def __str__(self):
        return str(self.__float__())

    def __repr__(self):
        return f"<Timer elapsed={self.elapsed}, ms={self.ms}>"


def format_string(argument):
    to_replace = (["-", "/"], [",", ""])
    for x, y in to_replace:
        argument = argument.replace(x, y)
    return argument


def convert_date(argument):
    argument = format_string(argument)
    formats = ("%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y", "%d/%m/%Y", "%b%d%y", "%b%d%Y", "%B%d%y", "%B%d%Y")

    for fmt in formats:
        try:
            return dt.strptime(argument, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return None
