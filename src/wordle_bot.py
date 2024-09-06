"""Discord related Cog"""

import discord
from utils.word_manager_instance import word_manager
from utils.logger import log_event


class WordleBot(discord.Bot):
    """Discord Wordle Bot"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.word_game = word_manager

    async def setup_hook(self):
        """Cog Hooks"""
        # Load cogs
        await self.load_extension("src.bot.cogs.wordle")
        print("Wordle cog loaded")

    async def on_ready(self):
        """On Ready details"""
        print(f"{self.user} has connected to Discord!")
        print(f"Bot is in {len(self.guilds)} guilds.")
        for guild in self.guilds:
            for channel in guild.text_channels:
                await guild.get_channel(channel.id).send('Hello! I am back online!')
                break

    async def on_guild_join(self, guild: discord.Guild):
        """On guild join"""
        log_event(
            "join",
            f"Bot has joined a new guild: {guild.name} (ID: {guild.id}), Members: {guild.member_count}",
        )
        owner = guild.owner
        if owner:
            try:
                await owner.send(f"Hello! Thanks for adding me to {guild.name}.")
            except discord.Forbidden:
                log_event(
                    "general",
                    f"Couldn't send welcome message to {owner.name} in guild: {guild.name}",
                )

    async def on_message(self, message: discord.Message):
        """on message on guild"""
        print('message is', message.content)