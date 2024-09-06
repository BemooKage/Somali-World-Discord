"""AutoComplete utils"""



import discord
from utils.word_manager_instance import word_manager

async def word_autocompletes(ctx: discord.AutocompleteContext):
    """Gets autocomplete words"""
    search = ctx.options['guess']
    if not search:
        return []
    words = word_manager.autocomplete(ctx.options['guess'])

    return words