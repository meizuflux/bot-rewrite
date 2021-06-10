from discord import ui, Interaction
import discord
from utils.buttons import StopButton

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
        else:
            base = page_number * self.per_page
            return self.entries[base:base + self.per_page]

class PageButton(ui.Button["ButtonPages"]):
    def __init__(self, func, *args, **kwargs) -> None:
        self.func = func
        super().__init__(style=discord.ButtonStyle.blurple, *args, **kwargs)

    async def callback(self, interaction: Interaction):
        await self.func()

class ButtonPages(ui.View):
    def __init__(self, source: ButtonSource, timeout: int=None):
        self._source = source
        self.current_page = 0
        super().__init__(timeout)

        async def func():
            await self.show_page(0)
        self.add_item(PageButton(func=func, label="First"))

        async def func():
            await self.show_checked_page(self.current_page - 1)
        self.add_item(PageButton(func=func, label="Previous"))

        async def func():
            await self.show_checked_page(self.current_page + 1)
        self.add_item(PageButton(func=func, label="Next"))

        async def func():
            await self.show_page(self._source.get_max_pages() - 1)
        self.add_item(PageButton(func=func, label="Last"))

        self.add_item(StopButton())


    async def show_page(self, page_number):
        page = await self._source.get_page(page_number)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        await self.message.edit(**kwargs)

    async def show_checked_page(self, page_number):
        max_pages = self._source.get_max_pages()
        try:
            if max_pages is None:
                # If it doesn't give maximum pages, it cannot be checked
                await self.show_page(page_number)
            elif max_pages > page_number >= 0:
                await self.show_page(page_number)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    async def interaction_check(self, interaction: Interaction):
        return interaction.user == self.ctx.author

    async def start(self, ctx):
        self.ctx = ctx
        await self._source._prepare_once()

        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        self.message = await ctx.send(**kwargs, view=self)

    async def _get_kwargs_from_page(self, page):
        value = await discord.utils.maybe_coroutine(self._source.format_page, self, page)
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            return { 'content': value, 'embed': None }
        elif isinstance(value, discord.Embed):
            return { 'embed': value, 'content': None }

class TestSource(ListButtonSource):
    async def format_page(self, menu, page):
        return page

test = TestSource([discord.Embed(title='1'), discord.Embed(title="2"), discord.Embed(title="3")], per_page=1)

