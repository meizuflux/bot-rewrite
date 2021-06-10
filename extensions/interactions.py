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
    "*crawls under the table and gives a boop to {user}!*",
)
bonk_fmt = "You've bonked {user} {amount} times! They've been bonked a total of {total} times."

bite_messages = ("*bites {user}*",)
bite_fmt = "You've bitten {user} {amount} times! They've been bitten a total of {total} times."

cuddle_messages = ("*you and {user} share a nice cuddle*",)
cuddle_fmt = "You've cuddled with {user} {amount} times, and they've been cuddled with a total of {total} times"


class Interactions(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    def construct_embed(
        self, method: str, _, user: discord.User
    ) -> Tuple[discord.File, discord.Embed]:
        embed = self.bot.embed(
            title=self.bot.random.choice(globals()[method + "_messages"]).format(
                user=user.display_name
            )
        )

        path = "./assets/" + method
        fn = self.bot.random.choice(listdir(path))
        file = discord.File(path + "/" + fn, filename=fn)
        embed.set_image(url="attachment://" + fn)

        return file, embed

    async def get_totals(
        self, method: str, initiator: discord.User, receiver: discord.User
    ) -> dict:
        query = """
            SELECT
                interactions.count AS amount, totals.count AS total
            FROM
               interactions
            INNER JOIN
                totals
                ON interactions.receiver = totals.snowflake
            WHERE
                initiator = $1 AND receiver = $2 AND interactions.method = $3 AND totals.method = $3
            """
        data = dict(await self.bot.pool.fetchrow(query, initiator.id, receiver.id, method))
        data.update({"user": receiver.display_name})
        return data

    async def update(self, method: str, initiator: discord.User, receiver: discord.User):
        query = """
            WITH total_update AS (
                INSERT INTO totals (method, snowflake) VALUES ($1, $3)
                ON CONFLICT (method, snowflake) DO UPDATE SET count = totals.count + 1
            )
            INSERT INTO interactions (method, initiator, receiver) VALUES ($1, $2, $3)
            ON CONFLICT (method, initiator, receiver) DO UPDATE
            SET count = interactions.count + 1
            """
        await self.bot.pool.execute(query, method, initiator.id, receiver.id)

    def invoke_check(self, verb: str, initiator: discord.User, receiver: discord.User):
        if initiator == receiver:
            raise commands.BadArgument(f"You can't {verb} yourself!")
        if receiver.bot is True and receiver.id != self.bot.user.id:
            raise commands.BadArgument(f"Bots don't like to be {verb}ed!")

    @core.command()
    async def bonk(self, ctx: CustomContext, user: discord.User):
        values = ("bonk", ctx.author, user)
        self.invoke_check(*values)
        await self.update(*values)
        file, embed = self.construct_embed(*values)
        embed.set_footer(text=bonk_fmt.format_map(await self.get_totals(*values)))
        await ctx.send(embed=embed, file=file)

    @core.command()
    async def bite(self, ctx: CustomContext, user: discord.User):
        values = ("bite", ctx.author, user)
        self.invoke_check(*values)
        await self.update(*values)
        file, embed = self.construct_embed(*values)
        embed.set_footer(text=bite_fmt.format_map(await self.get_totals(*values)))
        await ctx.send(embed=embed, file=file)

    @core.command()
    async def cuddle(self, ctx: CustomContext, user: discord.User):
        values = ("cuddle", ctx.author, user)
        self.invoke_check(*values)
        await self.update(*values)
        file, embed = self.construct_embed(*values)
        embed.set_footer(text=cuddle_fmt.format_map(await self.get_totals(*values)))
        await ctx.send(embed=embed, file=file)


def setup(bot):
    bot.add_cog(Interactions(bot))
