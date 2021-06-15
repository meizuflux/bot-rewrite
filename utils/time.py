import re
import time

from dateutil.relativedelta import relativedelta
from discord.ext import commands

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


def parse_time(ctx: CustomContext, time: str):
    argument = time.replace(" and ", "").replace(" ", "")
    match = TIME_REGEX.match(argument)
    if match is None or not match.group(0):
        raise commands.BadArgument("Invalid time provided.")
    data = {k: int(v) for k, v in match.groupdict(default=0).items()}
    return ctx.message.created_at + relativedelta(**data)


# from rapptz
def human_timedelta(dt, *, source=None, accuracy=3, suffix=True):
    now = source or dt.utcnow()
    # Microsecond free zone
    now = now.replace(microsecond=0)
    dt = dt.replace(microsecond=0)

    # This implementation uses relativedelta instead of the much more obvious
    # divmod approach with seconds because the seconds approach is not entirely
    # accurate once you go over 1 week in terms of accuracy since you have to
    # hardcode a month as 30 or 31 days.
    # A query like "11 months" can be interpreted as "!1 months and 6 days"
    if dt > now:
        delta = relativedelta(dt, now)
        suffix = ""
    else:
        delta = relativedelta(now, dt)
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
