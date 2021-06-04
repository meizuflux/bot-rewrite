import discord

from core.bot import CustomBot

intents = discord.Intents.default()
intents.members = True
intents.voice_states = False

flags = discord.MemberCacheFlags.from_intents(intents)

bot = CustomBot(
    command_prefix="none ",
    case_insensitive=True,
    intents=intents,
    member_cache_flags=flags,
    max_messages=750,
    owner_ids={809587169520910346}
)