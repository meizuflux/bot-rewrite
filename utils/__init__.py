import re

__all__ = ("MENTION_REGEX", "codeblock")

MENTION_REGEX = re.compile(r"<@!?(?P<id>[0-9]{15,20})>")


def codeblock(text: str, *, lang="py"):
    return f"```{lang}\n{text}```"
