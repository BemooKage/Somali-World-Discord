"""Main"""
import os
from dotenv import load_dotenv
from bot_instance import bot
from bot.cogs.wordle import WordleCog
from utils.logger import log_general_event

load_dotenv()
log_general_event('starting bot')
token = os.getenv("DISCORD_TOKEN")
wordle_cog = WordleCog(bot=bot)
bot.add_cog(wordle_cog)
bot.run(token)
