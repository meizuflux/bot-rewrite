from discord import ButtonStyle, Embed, Interaction, ui

from core.context import CustomContext
from utils.buttons import StopButton

EMOJIS = {
    "main": "<:osu:850783495386300416>"
}


class OsuProfileView(ui.View):
    embed: Embed

    def __init__(self, ctx: CustomContext, messages: dict):
        super().__init__()
        self.add_item(StopButton())
        self.ctx = ctx
        self.data = messages

    def construct_embed(self):
        self.embed = self.ctx.bot.embed(description=self.data["main"])
        self.embed.set_footer(text=self.data["footer"])
        self.embed.set_thumbnail(url=self.data["avatar_url"])

    async def start(self):
        self.construct_embed()
        await self.ctx.send(embed=self.embed, view=self)

    @ui.button(label="Main", style=ButtonStyle.primary, emoji=EMOJIS["main"])
    async def _main(self, button: ui.Button, interaction: Interaction):
        ...
