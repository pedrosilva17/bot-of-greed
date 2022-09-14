import os
import re
import asyncio
import time
import constants
import utils
import ygoapi as ygo
import disnake
from dotenv import load_dotenv
from disnake import Intents
from disnake.ui import Button, View
from disnake.ext import commands
from Paginate import CreatePaginator

"""
Initializing bot permissions and global variables, loading token and startup confirmation message.
"""
in_game = False
uptime = int(time.time())
intents = Intents.default()
intents.message_content = True
bot = commands.InteractionBot(command_prefix="yg_", intents=intents)

load_dotenv()
token = os.getenv("DISCORD_TOKEN")


@bot.event
async def on_ready():
    print("Ready to draw.")


@bot.slash_command(name="draw", description="Draw 2 cards, just like Pot of Greed.")
async def draw(ctx):
    """
    Randomly fetches two card images and joins them together, displaying them in an embed.
    Parameters:
    ----------
    :param ctx: The invocation context of the command.
    """
    await ctx.response.defer()
    embed, file = utils.embed_builder(ctx=ctx, embed_type="Draw")
    button = Button(label="Draw again", style=disnake.ButtonStyle.green, emoji="<:cards:973582121547485244>")
    view = View()
    view.add_item(button)
    button.callback = draw
    try:
        await ctx.edit_original_message(embed=embed, file=file, view=view)
    except disnake.errors.InteractionResponded:
        await ctx.send(file=file, embed=embed, view=view)
    return


@bot.slash_command(
    name="info",
    description="Some info about me."
)
async def info(ctx):
    """
    Sends a simple embed with information about the bot, such as the name of his creator (me) and his uptime, as well
    as some tips for the user.
    Parameters:
    ----------
    :param ctx: The invocation context of the command.
    """
    global uptime
    embed, file = utils.embed_builder(ctx=ctx, embed_type="Info", time=uptime)
    await ctx.send(embed=embed, file=file)


@bot.slash_command(
    name="guess",
    description="Given a card's text or artwork, guess its name. You have 90 seconds per game to guess.",
)
async def guess(ctx,
                mode: str = commands.Param(name="mode", description="The game mode to play.",
                                           choices=["Card Text", "Artwork"])
                ):
    """
    Guessing game that tests the user's ability to identify a card based on its description or artwork, depending on the
    value of the "mode" parameter.
    Parameters:
    ----------
    :param ctx: The invocation context of the command.
    :param mode: The game mode to play:
    - "Card Text": Guess the card through its description.
    - "Artwork": Guess the card through its artwork.
    """
    global in_game
    if in_game:
        await ctx.send("Hey, there's still a game in progress! Type 'quit' if you want to end it and then "
                       "start another.", ephemeral=True)
        return
    await ctx.response.defer()
    loading_emoji = disnake.utils.get(ctx.guild.emojis, name="level_spin")
    await ctx.send(f"Preparing the game... {loading_emoji}")
    embed, file, name, card = utils.embed_builder(ctx=ctx, embed_type="Guess", subtype=mode)

    try:
        button = Button(label="Hint", style=disnake.ButtonStyle.green, emoji=constants.emojis["red_question_mark"])
        view = View()
        view.add_item(button)

        async def show_hint(inter):
            """
            Upon clicking the "Hint" button, show the first letter of each word that composes the card name, as
            well as the number of letters, on the footer of the embed displaying the game.
            Parameters:
            ----------
            :param inter: The interaction invoking this function (the click on the button).
            """
            hint = ""
            hint_list = name.split()
            for word in hint_list:
                hint += word[0] + re.sub('[A-z]', '_ ', word[1:]) + ' '
            embed.set_footer(text=f"Hint: {hint} | Type: {card['data']['type']}")
            await inter.response.edit_message(embed=embed, view=view)
            return

        async def game_loop():
            """
            Loop that controls the flow of the game. There are 5 lives shared by every member that decides to guess,
            and if they are all spent, the game ends. Guessing the card name or typing "quit" produces the same result.
            """
            global in_game
            in_game = True
            tries = 5
            while in_game:
                answer = await bot.wait_for('message')
                if not answer.author.bot and answer.channel == ctx.channel and answer.author.id == ctx.author.id:
                    if name.lower() == answer.content.lower():
                        await answer.reply(f"{answer.author.mention} got it right! Well done.")
                        in_game = False
                        break
                    match answer.content.lower():
                        case "quit":
                            await answer.reply(f"{answer.author.mention} ended the game. The answer is {name}.")
                            in_game = False
                        case _:
                            tries -= 1
                            match tries:
                                case 1:
                                    await ctx.send(f"{answer.author.mention}, wrong! Last chance...")
                                case 0:
                                    await ctx.send(f"Game over! The answer is {name}.")
                                    in_game = False
                                case _:
                                    await ctx.send(f"{answer.author.mention}, wrong! {tries} tries left.")
                            await asyncio.sleep(0.3)

        button.callback = show_hint
        await ctx.edit_original_message(content="", embed=embed, view=view, file=file)
        await asyncio.sleep(0.3)
        await asyncio.wait_for(game_loop(), timeout=90)

    except asyncio.TimeoutError:
        await ctx.send(f"Time's up! The answer is {name}.")
        in_game = False
    return


@bot.slash_command(
    name="search",
    description="Search for cards using multiple filters.",
)
async def search(ctx,
                 name: str = commands.Param(default=None, name="name", description="Filter by name (one card)."),
                 name_multi: str = commands.Param(default=None, name="name_multi",
                                                  description="Filter by name (one or more cards)."),
                 _type: str = commands.Param(default=None, name="type", description="Filter by card type."),
                 race: str = commands.Param(default=None, name="race", description="Filter by race."),
                 attribute: str = commands.Param(default=None, name="attribute",
                                                 description="Filter by card attribute."),
                 attack: str = commands.Param(default=None, name="attack", description="Filter by attack points."),
                 defense: str = commands.Param(default=None, name="defense", description="Filter by defense points."),
                 level_rank: str = commands.Param(default=None, name="level_rank", description="Filter by level/rank."),
                 link: str = commands.Param(default=None, name="link", description="Filter by link value."),
                 link_marker: str = commands.Param(default=None, name="link_markers",
                                                   description="Filter by link markers."),
                 scale: str = commands.Param(default=None, name="scale", description="Filter by Pendulum Scale value."),
                 sort: str = commands.Param(default=None, name="sort_by", description="Sort the results in case more "
                                                                                      "than one card is found.",
                                            choices=["Attack", "Defense", "Name", "Type", "Level", "ID", "New",
                                                     "Relevance"]),
                 ):
    """
    Searches the database for cards, using a variety of filters and sorting options, and calls an embed generator
    function to display the results in a user-friendly and appealing manner.
    Parameters:
    ----------
    :param ctx: The invocation context of the command.
    :param name: Name to filter with, that can show at most one card.
    :param name_multi: Name to filter with, that can show one or more cards (assuming there are no errors).
    :param _type: Card type(s) to filter with.
    :param race: Card "race(s)" to filter with.
    :param attribute: Card attribute(s) to filter with.
    :param attack: Attack value to filter with.
    :param defense: Defense value to filter with.
    :param level_rank: Level/rank value to filter with.
    :param link: Link value to filter with.
    :param link_marker: Link marker(s) to filter with.
    :param scale: Pendulum scale value to filter with.
    :param sort: Parameter to sort by.
    """
    loading_emoji = disnake.utils.get(ctx.guild.emojis, name="level_spin")
    await ctx.send(f"Searching... {loading_emoji}")
    filters = {"name": name, "fname": name_multi, "type": _type, "race": race, "attribute": attribute, "atk": attack,
               "def": defense, "level": level_rank, "link": link, "linkmarker": link_marker, "scale": scale, "sort": sort}
    response = ygo.query(filters)
    embed, file = utils.embed_builder(ctx=ctx, embed_type="Search", response=response, subtype="Card")

    """
    Checks to verify the type of the variable "embed": Error, single embed or list of embeds.
    """
    if embed == "err":
        embed = disnake.Embed(title="An error has occurred!", description=response["error"])
        await ctx.edit_original_message(content="No luck...", embed=embed)
    elif isinstance(embed, disnake.Embed):
        if not file:
            await ctx.edit_original_message(content="Found it!", embed=embed)
        else:
            await ctx.edit_original_message(content="Found it!", embed=embed, file=file)
    else:
        author_id = ctx.author.id
        view = CreatePaginator(ctx, embed, author_id, len(embed))
        await ctx.edit_original_message(content="Here's a list of the results.", embed=embed[0], view=view)
    return


@bot.slash_command(
    name="guide",
    description="Get help regarding less straightforward commands.",
)
async def guide(ctx,
                command: str = commands.Param(name="command", description="The command to be checked.",
                                              choices=["Guess", "Search"])
                ):
    """
    Sends embed(s) with more detailed explanations of the chosen command in the "command" parameter.
    Parameters:
    ----------
    :param ctx: The invocation context of the command.
    :param command: The command to display more information about.
    """
    match command:
        case "Guess":
            embed, file = utils.embed_builder(ctx=ctx, embed_type="Guess", subtype="Guide")
            await ctx.send(embed=embed, file=file)
            return
        case "Search":
            embed, file = utils.embed_builder(ctx=ctx, embed_type="Search", subtype="Guide")
            author_id = ctx.author.id
            view = CreatePaginator(ctx, embed, author_id, len(embed), False)
            await ctx.send(embed=embed[0], file=file, view=view)
            return


bot.run(token)
