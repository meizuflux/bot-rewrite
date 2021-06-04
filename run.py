import os

import discord

from core.bot import CustomBot, get_prefix
from core.config import token

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    intents.voice_states = False

    flags = discord.MemberCacheFlags.from_intents(intents)

    bot = CustomBot(
        command_prefix=get_prefix,
        case_insensitive=True,
        intents=intents,
        member_cache_flags=flags,
        max_messages=750,
        owner_ids={809587169520910346},
    )

    os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
    os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
    os.environ["JISHAKU_HIDE"] = "True"

    bot.run(token)
