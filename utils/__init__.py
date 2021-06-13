import re

__all__ = ("MENTION_REGEX",)

MENTION_REGEX = re.compile(r"<@!?(?P<id>[0-9]{15,20})>")
