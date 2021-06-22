import asyncio
from datetime import datetime as dt
from random import choice
from typing import List, Optional

import discord
from discord import utils
from discord.ext import commands

import core
from core.bot import CustomBot
from core.context import CustomContext
from utils.formats import plural
from utils.time import parse_time, utcnow

__all__ = ("setup",)

tadas = ("<a:tada1:856337025666121768>", "<a:tada2:856679655117553695>", "<a:tada3:856679655225425921>",
         "<a:tada4:856679655314685954>", "<a:tada5:856679655422427136>", "<a:tada6:856679655427801168>",
         "<a:tada7:856679655535935518>")


def random_tada():
    return choice(tadas)


async def get_channel(ctx: CustomContext, argument: str) -> Optional[discord.TextChannel]:
    try:
        channel = await commands.TextChannelConverter().convert(ctx, argument)
    except commands.ChannelNotFound:
        await ctx.send(f"{random_tada()} Sorry, I couldn't find a channel from your input.")
        return None

    permissions = channel.permissions_for(ctx.me)
    if permissions.send_messages is False:
        await ctx.send(f"{random_tada()} I'm missing the permission to send messages in that channel, "
                       f"please make sure that is enabled, then retry. ")
        return None
    if permissions.embed_links is False:
        await ctx.send(f"{random_tada()} I'm missing the permission to send an embed in that channel, "
                       f"please make sure that is enabled, then retry. ")
        return None
    if permissions.embed_links is False:
        await ctx.send(f"{random_tada()} I'm missing the permission to add reactions in that channel, "
                       f"please make sure that is enabled, then retry. ")
        return None

    return channel


async def get_expiration(ctx: CustomContext, argument: str) -> Optional[dt]:
    try:
        expires = parse_time(ctx, argument, _add_now=True)
    except commands.BadArgument as err:
        await ctx.send(f"{random_tada()} {str(err)}")
        return None

    return expires


async def get_prize(ctx: CustomContext, argument: str) -> Optional[str]:
    if len(argument) >= 256:
        await ctx.send(f"{random_tada()} The prize must be less than 256 characters long, sorry. ;-;")
        return None

    return argument


async def get_mex_winners(ctx: CustomContext, argument: str) -> Optional[int]:
    if not argument.isdigit():
        await ctx.send(f"{random_tada()} Please send a number. ;-;")
        return None
    length = len(argument)
    if length > 15 or length < 1:
        await ctx.send(f"{random_tada()} Max winners can't be more than 15, and must be greater or equal to 0.")
        return None

    return int(argument)


async def wait_for(ctx: CustomContext) -> Optional[str]:
    check = lambda m: m.author == ctx.author and m.channel == ctx.channel
    try:
        message: discord.Message = await ctx.bot.wait_for("message", check=check, timeout=120)
    except asyncio.TimeoutError:
        await ctx.send(
            f"{random_tada()} {ctx.author.mention}, hi, sorry, you need to answer each question within 2 minutes.")
        return None

    if message.content.lower().strip() == 'cancel':
        await ctx.send(f"{random_tada()} Cancelled.")
        return None

    return message.content


class Giveaways(commands.Cog):
    def __init__(self, bot: CustomBot):
        self.bot = bot

    @core.command(
        aliases=("gcreate", "giveawaycreate", "giveaway_create", "cgiveaway")
    )
    async def create_giveaway(self, ctx: CustomContext):
        timer = self.bot.get_cog("Reminders")
        if timer is None:
            return await ctx.send("This functionality is not available currently.")

        await ctx.send(f"{random_tada()} Ok, lets create your giveaway. "
                       f"First, what channel do you want your giveaway to be in? "
                       f"Also, you can type `cancel` at anytime to cancel the process.\n\n"
                       f"`Please mention a channel in this server.`")
        resp = await wait_for(ctx)
        if resp is None:
            return
        channel = await get_channel(ctx, resp)
        if channel is None:
            return

        winners = 1

        await ctx.send(
            f"{random_tada()} Sweet! {winners} {plural('winner(s)', winners)} it is. Lastly, please send the prize of this giveaway."
            f"\n\n`Please send the giveaway prize. It must be less than 256 characters. "
            f"You can also use basic markdown in your response.`")
        prize = await wait_for(ctx)
        if prize is None:
            return

        await ctx.send(f"{random_tada()} Nice, the prize for the giveaway will be {prize}. "
                       f"Now, when do you want the giveaway to expire?\n\n"
                       f"`Please send a time in the future when you want the giveaway to expire. You can send something like "
                       f"'30 minutes' or a date in MM/DD/YY format. (I also accept a few more formats). "
                       f"This will start the game.`")
        resp = await wait_for(ctx)
        if resp is None:
            return
        expires = await get_expiration(ctx, resp)
        if expires is None:
            return

        selected_tada = random_tada()

        embed = self.bot.embed(
            title=prize,
            description=(
                f"React with {selected_tada} to enter.\n"
                f"There will be {winners} {plural('winner(s)', winners)}."
            ),
            color=discord.Color.blurple(),
            timestamp=expires
        )
        embed.set_footer(text=f"Ends at ")
        message = await channel.send(embed=embed)
        await message.add_reaction(selected_tada)

        m = await ctx.send(f"{random_tada()} Giveaway has been started in {channel.mention}!")

        data = {
            "message": message.id,
            "channel": channel.id,
            "prize": prize,
            "winners": winners,
            "emoji": int(selected_tada.rstrip(">").split(":")[2])
        }
        await timer.create_timer(
            "giveaway", utcnow(), expires, data
        )
        await m.add_reaction("✅")

    async def get_winners(self, message: discord.Message, *, emoji: str, winners: int) -> List[discord.Member]:
        if not message.reactions:
            return []

        reaction = discord.utils.get(message.reactions, emoji__id=emoji)
        users = [user async for user in reaction.users() if user.bot is False]

        return self.bot.random.sample(users, min(len(users), winners))

    @commands.Cog.listener()
    async def on_giveaway_complete(self, reminder):
        print(reminder)
        data = reminder["data"]
        try:
            channel: discord.TextChannel = self.bot.get_channel(data["channel"]) or (
                await self.bot.fetch_channel(data["channel"]))
        except discord.HTTPException:
            return

        try:
            message = utils.get(self.bot.cached_messages, id=data["message"]) or (
                await channel.fetch_message(data["message"]))
        except discord.HTTPException:
            return

        winners = await self.get_winners(message, emoji=data["emoji"], winners=data["winners"])
        print(winners)


def setup(bot: CustomBot):
    bot.add_cog(Giveaways(bot))
