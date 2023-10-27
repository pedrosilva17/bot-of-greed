import disnake
from disnake.utils import get

import constants
import database
import utils


class CreatePaginator(disnake.ui.View):
    """A paginator that organizes embeds and allows easy interaction with buttons.

    Args:
      ctx: The invocation context of this paginator.
      embeds: A list of embeds in the paginator, starting from the first embed.
      author: The ID of the user that called the paginator. Only that user can
      interact with the paginator, unless this parameter is 0, in which case everyone can use it. Defaults to 0.
      size: The number of embeds in the paginator. Defaults to 1.
      has_dropdown: A boolean value that determines if the paginator needs a dropdown menu. Defaults to true.

    Returns:

    """

    def __init__(
        self,
        ctx,
        embeds: list,
        author: int = 0,
        size: int = 1,
        has_dropdown: bool = True,
    ):
        super().__init__()
        self.ctx = ctx
        self.embeds = embeds
        self.author = author
        self.index = 0
        self.size = size
        self.has_dropdown = has_dropdown
        self.select = disnake.ui.Select(options=[])
        dict_embed = self.embeds[0].to_dict()
        if self.has_dropdown:
            for field in dict_embed["fields"]:
                emoji_name = (
                    field["value"]
                    .split("|")[1]
                    .strip()
                    .lower()
                    .replace(" ", "_")
                    .replace("-", "_")
                )
                emoji = get(self.ctx.guild.emojis, name=emoji_name)
                self.select.append_option(
                    disnake.SelectOption(
                        label=field["name"], emoji=emoji, description=field["value"]
                    )
                )
            self.select.callback = self.single_search
            self.add_item(self.select)

    async def single_search(self, inter):
        """
        Sends an individual embed with info about the card chosen in the dropdown menu.

        Args:
            inter:
        """
        response = database.query({"name": self.select.values[0]})
        embed = utils.search_wrapper(self.ctx, response)
        await inter.response.send_message(embed=embed, file=embed.file)

    def out_of_bounds(self, bound: str):
        """Checks if the current index is out of bounds after moving.

        Args:
          bound: str:
        Returns: A boolean that is false if the index value is less than the number of pages -1 on the right bound
        or the index value is greater than zero on the left bound.
        """
        return ((self.index <= 0) and bound == "left") or (
            (self.index >= self.size - 1) and bound == "right"
        )

    def draw_dropdown(self):
        """
        Draws the dropdown menu, dynamically updated after changing pages.
        """
        if self.has_dropdown:
            self.remove_item(self.children[-1])
            self.select = disnake.ui.Select(options=[])
            dict_embed = self.embeds[self.index].to_dict()
            for field in dict_embed["fields"]:
                emoji_name = (
                    field["value"]
                    .split("|")[1]
                    .strip()
                    .lower()
                    .replace(" ", "_")
                    .replace("-", "_")
                )
                emoji = get(self.ctx.guild.emojis, name=emoji_name)
                self.select.append_option(
                    disnake.SelectOption(
                        label=field["name"], emoji=emoji, description=field["value"]
                    )
                )
            self.select.callback = self.single_search
            self.add_item(self.select)
        return

    """
    Collection of buttons that allow quick/slow movement through the paginator or its deletion, keeping the text chat
    clean.
    """

    @disnake.ui.button(
        emoji=constants.emojis["fast_reverse"], style=disnake.ButtonStyle.grey
    )
    async def rewind(self, button, inter):
        if self.out_of_bounds("left"):
            return await inter.send("You are on the first page.", ephemeral=True)
        elif inter.author.id != self.author and self.author != 0:
            return await inter.send(
                "You cannot interact with these buttons.", ephemeral=True
            )
        elif self.index >= 10:
            self.index -= 10
            self.draw_dropdown()
            await inter.response.edit_message(embed=self.embeds[self.index], view=self)
        else:
            self.index = 0
            self.draw_dropdown()
            await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(
        emoji=constants.emojis["reverse"], style=disnake.ButtonStyle.grey
    )
    async def previous(self, button, inter):
        if self.out_of_bounds("left"):
            return await inter.send("You are on the first page.", ephemeral=True)
        elif inter.author.id != self.author and self.author != 0:
            return await inter.send(
                "You cannot interact with these buttons.", ephemeral=True
            )
        else:
            self.index -= 1
            self.draw_dropdown()
            await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(
        emoji=constants.emojis["wastebasket"], style=disnake.ButtonStyle.red
    )
    async def delete(self, button, inter):
        if inter.author.id != self.author and self.author != 0:
            return await inter.send(
                "You cannot interact with these buttons.", ephemeral=True
            )
        return await inter.message.delete()

    @disnake.ui.button(emoji=constants.emojis["play"], style=disnake.ButtonStyle.grey)
    async def next(self, button, inter):
        if self.out_of_bounds("right"):
            return await inter.send("You are on the last page.", ephemeral=True)
        elif inter.author.id != self.author and self.author != 0:
            return await inter.send(
                "You cannot interact with these buttons.", ephemeral=True
            )
        else:
            self.index += 1
            self.draw_dropdown()
            await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @disnake.ui.button(
        emoji=constants.emojis["fast_forward"], style=disnake.ButtonStyle.grey
    )
    async def skip(self, button, inter):
        if self.out_of_bounds("right"):
            return await inter.send("You are on the last page.", ephemeral=True)
        elif inter.author.id != self.author and self.author != 0:
            return await inter.send(
                "You cannot interact with these buttons.", ephemeral=True
            )
        elif self.index <= self.size - 11:
            self.index += 10
            self.draw_dropdown()
            await inter.response.edit_message(embed=self.embeds[self.index], view=self)
        else:
            self.index = self.size - 1
            self.draw_dropdown()
            await inter.response.edit_message(embed=self.embeds[self.index], view=self)
