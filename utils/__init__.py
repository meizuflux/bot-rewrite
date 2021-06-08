import re

MENTION_REGEX = re.compile(r"<@!?(?P<id>[0-9]{15,20})>")
