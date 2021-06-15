from collections import OrderedDict

import discord
from discord import Interaction, ui
from discord.ext import commands

from utils.buttons import StopButton


class MenuError(Exception):
    pass


class CannotEmbedLinks(MenuError):
    def __init__(self):
        super().__init__("Bot does not have embed links permission in this channel.")


class CannotSendMessages(MenuError):
    def __init__(self):
        super().__init__("Bot cannot send messages in this channel.")


class CannotReadMessageHistory(MenuError):
    def __init__(self):
        super().__init__("Bot does not have Read Message History permissions in this channel.")


class ButtonSource:
    async def _prepare_once(self):
        try:
            self.__prepare
        except AttributeError:
            await self.prepare()
            self.__prepare = True

    async def prepare(self):
        return

    def is_paginating(self):
        raise NotImplementedError

    def get_max_pages(self):
        return None

    async def get_page(self, page_number):
        raise NotImplementedError

    async def format_page(self, menu, page):
        raise NotImplementedError


class ListButtonSource(ButtonSource):
    def __init__(self, entries, *, per_page):
        self.entries = entries
        self.per_page = per_page

        pages, left_over = divmod(len(entries), per_page)
        if left_over:
            pages += 1

        self._max_pages = pages

    def is_paginating(self):
        return len(self.entries) > self.per_page

    def get_max_pages(self):
        return self._max_pages

    async def get_page(self, page_number):
        if self.per_page == 1:
            return self.entries[page_number]
        base = page_number * self.per_page
        return self.entries[base : base + self.per_page]


class MenuButton(ui.Button):
    def __init__(self, func, **kwargs) -> None:
        self.cls = None
        self.func = func
        super().__init__(style=discord.ButtonStyle.blurple, **kwargs)

    async def callback(self, interaction: Interaction):
        await self.func(self.cls, interaction)


def button(**kwargs):
    def decorator(func):
        func.__button_kwargs__ = kwargs
        return func

    return decorator


class _MenuMeta(type):
    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # This is needed to maintain member order for the buttons
        return OrderedDict()

    def __new__(cls, name, bases, attrs, **kwargs):
        buttons = []
        new_cls = super().__new__(cls, name, bases, attrs)

        for elem, value in attrs.items():
            try:
                value.__button_kwargs__
            except AttributeError:
                continue
            else:
                buttons.append(value)

        new_cls.__buttons__ = buttons
        return new_cls

    def get_buttons(cls):
        return [MenuButton(func, **func.__button_kwargs__) for func in cls.__buttons__]


class ButtonMenu(ui.View, metaclass=_MenuMeta):
    ctx: commands.Context

    def __init__(self, *, timeout=180.0, delete_message_after=False):
        super().__init__(timeout)
        self.delete_message_after = delete_message_after
        self.message = None

        self._buttons = self.__class__.get_buttons()

        for _button in self._buttons:
            _button.cls = self
            self.add_item(_button)

    def should_add_reactions(self):
        return len(self._buttons)

    def _verify_permissions(self, ctx, channel, permissions):
        if not permissions.send_messages:
            raise CannotSendMessages()

        if self.should_add_reactions() and not permissions.read_message_history:
            raise CannotReadMessageHistory()

    async def start(self, ctx: commands.Context, *, channel=None, **send_kwargs):
        self.ctx = ctx

        channel = channel or ctx.channel
        is_guild = isinstance(channel, discord.abc.GuildChannel)
        me = channel.guild.me if is_guild else ctx.bot.user
        permissions = channel.permissions_for(me)
        self._verify_permissions(ctx, channel, permissions)

        self.message = await self.send_initial_message(channel, **send_kwargs)

    async def send_initial_message(self, channel, **send_kwargs):
        view = send_kwargs.pop("view", self)
        await channel.send(**send_kwargs, view=view)


class ButtonPages(ButtonMenu):
    def __init__(self, source: ButtonSource, **kwargs):
        self._source = source
        self.current_page = 0
        super().__init__(**kwargs)

        self.add_item(StopButton())

    async def show_page(self, interaction, page_number):
        page = await self._source.get_page(page_number)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        await interaction.response.edit_message(**kwargs)

    async def show_checked_page(self, interaction, page_number):
        max_pages = self._source.get_max_pages()
        try:
            if max_pages is None or max_pages > page_number >= 0:
                # If it doesn't give maximum pages, it cannot be checked
                await self.show_page(interaction, page_number)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    async def interaction_check(self, interaction: Interaction):
        return interaction.user == self.ctx.author

    async def start(self, ctx, *, channel=None):
        self.ctx = ctx
        await self._source._prepare_once()

        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        await super().start(ctx, channel=channel or ctx.channel, **kwargs)

    async def _get_kwargs_from_page(self, page):
        value = await discord.utils.maybe_coroutine(self._source.format_page, self, page)
        kwargs = {}
        if isinstance(value, dict):
            kwargs = value
        elif isinstance(value, str):
            kwargs = {"content": value, "embed": None}
        elif isinstance(value, discord.Embed):
            kwargs = {"embed": value, "content": None}
        if kwargs:
            kwargs["view"] = self
        return kwargs

    @button(label="<<")
    async def first(self, interaction: Interaction):
        await self.show_page(interaction, 0)

    @button(label="<")
    async def previous(self, interaction: Interaction):
        await self.show_checked_page(interaction, self.current_page - 1)

    @button(label=">")
    async def next(self, interaction: Interaction):
        await self.show_checked_page(interaction, self.current_page + 1)


class TestSource(ListButtonSource):
    async def format_page(self, menu, page):
        return page


test = TestSource(
    [discord.Embed(title="1"), discord.Embed(title="2"), discord.Embed(title="3")], per_page=1
)
