import os

import discord

from core.bot import CustomBot
from core.config import token

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True

    flags = discord.MemberCacheFlags.from_intents(intents)

    bot = CustomBot(
        skip_after_prefix=True,
        case_insensitive=True,
        intents=intents,
        member_cache_flags=flags,
        max_messages=750,
        owner_id=809587169520910346,
    )

    os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
    os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
    os.environ["JISHAKU_HIDE"] = "True"
    os.environ["PYTHONIOENCODING"] = "UTF-8"

    bot.run(token)
