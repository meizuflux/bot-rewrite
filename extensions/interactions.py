from os import listdir
from typing import Tuple

import discord
from discord.ext import commands

import core
from core.bot import CustomBot
from core.context import CustomContext

bonk_messages = (
    "*bonks {user} on the nose lol*",
    "*sneaks behind {user} and bonks them!*",
    "*crawls under the table and gives a boop to {user}!*"
)
bonk_fmt = "You've bonked {user} {amount} times now! They've been bonked a total of {total} times."


class Interactions(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    def construct_embed(self, user: discord.User, *, _type: str) -> Tuple[discord.File, discord.Embed]:
        embed = self.bot.embed(
            title=self.bot.random.choice(
                globals()[_type + "_messages"]).format(user=user.display_name)
        )
        path = "./assets/" + _type
        fn = self.bot.random.choice(listdir(path))
        file = discord.File(path + "/" + fn, filename=fn)
        embed.set_image(url="attachment://" + fn)

        return file, embed

    async def get_totals(self, initiator: discord.User, receiver: discord.User) -> dict:
        query = (
            """
            SELECT
                interactions.count AS amount, totals.count AS total
            FROM
               interactions
            INNER JOIN
                totals
                ON interactions.receiver = totals.snowflake
            WHERE
                initiator = $1 AND receiver = $2
            """
        )
        data = await self.bot.pool.fetchrow(query, initiator.id, receiver.id)
        return data

    @core.command()
    async def bonk(self, ctx: CustomContext, user: discord.User):
        file, embed = self.construct_embed(user, _type="bonk")
        await ctx.send(embed=embed, file=file)

def setup(bot):
    bot.add_cog(Interactions(bot))
