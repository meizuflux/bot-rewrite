import asyncio
from datetime import datetime, timedelta

from discord.ext import commands
from humanize import precisedelta

import core
from core.bot import CustomBot
from core.config import osu_client_id, osu_client_secret
from core.context import CustomContext
from utils.buttons.osu import OsuProfileView
from utils.decos import wait_until_ready

API_URL = "https://osu.ppy.sh/api/v2"


class Osu(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        self.emoji = "<:osu:850783495386300416>"
        self.show_subcommands = True

        self.headers = {"Authorization": None}

        bot.loop.create_task(self.acquire_bearer_token())

    @wait_until_ready()
    async def acquire_bearer_token(self):
        url = "https://osu.ppy.sh/oauth/token"
        data = {
            "client_id": osu_client_id,
            "client_secret": osu_client_secret,
            "grant_type": "client_credentials",
            "scope": "public",
        }
        while not self.bot.is_closed():
            async with self.bot.session.post(url, json=data) as r:
                data = await r.json()
            self.headers["Authorization"] = "Bearer " + data["access_token"]
            await asyncio.sleep(data["expires_in"])

    async def get_user(self, user: str):
        url = API_URL + f"/users/{user}/osu?key=username"
        async with self.bot.session.get(url, headers=self.headers) as r:
            if r.status == 404:
                raise commands.BadArgument("Could not find anything from that query.")
            data = await r.json()
        return data

    @core.command()
    async def osu(self, ctx: CustomContext, query: str):
        data = await self.get_user(query)
        stats = data.get("statistics", {})
        username = data.get("username")
        join = datetime.fromisoformat(data.get("join_date")).strftime("%b %d %Y")
        plays_with = data.get("playstyle") or ["This user has not set what they play with."]
        ranks = stats.get("grade_counts")
        time_played = precisedelta(
            timedelta(seconds=stats.get("play_time")),
            suppress=["months", "years", "days"],
            format="%0.0f",
            minimum_unit="minutes",
        )
        _global = stats['global_rank'] or 0
        _country = stats.get("rank", {})['country'] or 0
        data = {
            "username": username,
            "url": "https://osu.ppy.sh/users/" + str(data.get("id")),
            "avatar_url": data.get(
                "avatar_url", "https://osu.ppy.sh/images/layout/avatar-guest.png"
            ),
            "footer": f"{username} started playing osu! on {join}",
            "Main": (
                f"**PP:** `{stats.get('pp')}`\n"
                f"**Global Rank:** `{_global:,d}`\n"
                f"**Country Rank:** :flag_{data.get('country_code').lower()}: `{_country:,d}`\n"
                f"**Replays Watched by Others:** `{stats.get('replays_watched_by_others', 0):,d}`\n"
                f"**First Place Ranks:** `{data.get('scores_first_count'):,d}`\n"
                f"**Average Accuracy:** `{(stats.get('hit_accuracy', 0) / 100):.2%}`\n"
                f"**Plays With:** `{', '.join(i.capitalize() for i in plays_with)}`\n"
                f"**Play Time:** `{time_played}`"
            ),
            "Socials": (
                f"**Discord:** `{data.get('discord') or 'This user has not set their Discord'}`\n"
                f"**Website:** `{data.get('website') or 'This user has not set their website'}`\n"
                f"**Twitter:** `{data.get('twitter') or 'This user has not set their Twitter'}`\n"
                f"**Occupation:** `{data.get('occupation') or 'This user has not set their occupation'}`\n"
                f"**Location:** `{data.get('location') or 'This user has not set their location'}`\n"
                f"**Forum Posts:** `{data.get('post_count', 0):,d}`"
            ),
            "Scores": (
                f"**SS Ranks:** `{ranks.get('ss', 0):,d}`\n"
                f"**S Ranks:** `{ranks.get('s', 0):,d}`\n"
                f"**A Ranks:** `{ranks.get('a', 0):,d}`\n"
                f"**Total Score:** `{stats.get('total_score', 0):,d}`\n"
                f"**Ranked Score:** `{stats.get('ranked_score', 0):,d}`\n"
                f"**Play Count:** `{stats.get('play_count', 0):,d}`\n"
                f"**Total Hits:** `{stats.get('total_hits', 0):,d}`\n"
                f"**Maximum Combo:** `{stats.get('maximum_combo', 0):,d}`"
            ),
        }
        view = OsuProfileView(ctx, data)
        await view.start()


def setup(bot):
    bot.add_cog(Osu(bot))
