import re

MENTION_REGEX = re.compile(r"<@!?(?P<id>[\d]+)>")
