from discord import ButtonStyle, Embed, Interaction, ui

from core.context import CustomContext
from utils.buttons import StopButton

EMOJIS = {
    "Main": "<:osu:850783495386300416>",
    "Socials": "<:socials:851127959758176256>",
    "Scores": "<:catshrug:851131304736194600>",
}


class OsuButton(ui.Button["OsuProfileView"]):
    def __init__(self, label: str):
        super().__init__(label=label, emoji=EMOJIS[label], style=ButtonStyle.blurple)

    async def callback(self, interaction: Interaction):
        self.view.embed.description = self.view.data[self.label]
        await interaction.response.edit_message(embed=self.view.embed)


class OsuProfileView(ui.View):
    embed: Embed

    def __init__(self, ctx: CustomContext, messages: dict):
        super().__init__()
        self.ctx = ctx
        self.data = messages

        for i in EMOJIS:
            self.add_item(OsuButton(label=i))
        self.add_item(StopButton())

    def construct_embed(self):
        self.embed = self.ctx.bot.embed(
            title=f"{self.data['username']}'s osu! profile",
            description=self.data["Main"],
            url=self.data["url"],
        )
        self.embed.set_footer(text=self.data["footer"])
        self.embed.set_thumbnail(url=self.data["avatar_url"])

    async def start(self):
        self.construct_embed()
        await self.ctx.send(embed=self.embed, view=self)
