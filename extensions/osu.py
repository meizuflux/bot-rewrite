import asyncio

from discord.ext import commands

import core
from core.bot import CustomBot
from core.config import osu_client_id, osu_client_secret
from core.context import CustomContext
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
            "scope": "public"
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
        desc = (
            f"**PP:** `{stats.get('pp')}`\n"
            f"**Global Rank:** `{stats.get('global_rank', 0):,d}`\n"
            f"**Average Accuracy:** `{(stats.get('hit_accuracy', 0) / 100):.2%}`"
        )

        embed = self.bot.embed(title=f"Osu! Profile For {data.get('username')}", description=desc, url="https://osu.ppy.sh/users/" + str(data.get("id")))
        embed.set_thumbnail(url=data.get("avatar_url", "https://osu.ppy.sh/images/layout/avatar-guest.png"))
        if (discord := data.get("discord")) is not None:
            embed.set_footer(text="Discord: " + discord)

        await ctx.send(embed=embed)




def setup(bot):
    bot.add_cog(Osu(bot))
