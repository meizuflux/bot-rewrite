from typing import Optional, Union

import discord


class StopButton(discord.ui.Button):
    """A button that deletes the message when pressed."""

    def __init__(
        self,
        *,
        style: discord.ButtonStyle = discord.ButtonStyle.red,
        label: Optional[str] = "Stop",
        disabled: bool = False,
        custom_id: Optional[str] = None,
        emoji: Optional[Union[str, discord.PartialEmoji]] = None,
        row: Optional[int] = None,
    ):
        # we override some things so I don't have to pass in the same stuff every time
        super().__init__(
            style=style, label=label, disabled=disabled, custom_id=custom_id, emoji=emoji, row=row
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()
