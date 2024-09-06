"""Discord Cog for Wordle game"""

from collections import defaultdict

import discord
from discord.ext import commands, tasks

from game.wordle_game import WordleGame
from utils.autocompletes import word_autocompletes


class WordleCog(discord.Cog):
    """Main Cog for Wordle GAme"""

    def __init__(self, bot):
        self.bot = bot
        self.word_manager = bot.word_game
        self.game = WordleGame(self.word_manager)
        self.scores = defaultdict(int)
        self.change_word.start()

    def cog_unload(self):
        self.change_word.cancel()

    @tasks.loop(minutes=15)  # Run daily every 15 mins
    async def change_word(self):
        self.game.new_word()
        print(f"New word set: {self.game.guess_word}")
        self.send_new_word_message()
        self.handle_current_guesses()
        self.game.reset_guesses()  # Reset guesses for the new word

    async def handle_current_guesses(self):
        """Removes all guesses from users not completed and autoset their scores"""
        raise NotImplementedError
    
    async def send_new_word_message(self):
        """When word is changed it sends new word notification"""
        raise NotImplementedError

    @commands.slash_command(
        name="wordle", description="Make a guess in the Wordle game"
    )
    async def play_wordle(
        self,
        ctx: discord.ApplicationContext,
        guess: discord.Option(
            str,
            "Your 5-letter word guess",
            autocomplete=word_autocompletes,
            required=True,
        ),  # type: ignore
    ):
        """Guess for current guess_word word"""
        result, is_correct = self.game.guess(ctx.author.id, guess)

        if is_correct:
            self.scores[ctx.author.id] += 1

        if is_correct:
            await ctx.respond(result, ephemeral=True)
        else:
            await ctx.respond(result)

    @commands.slash_command(
        name="wordlerules", description="Display the rules of the Wordle game"
    )
    async def wordle_rules(self, ctx: discord.ApplicationContext):
        """Returns wordle rules"""
        rules = (
            "Welcome to Discord Wordle!\n"
            "- A new word is chosen every day at midnight.\n"
            "- You have 6 attempts to guess the 5-letter word.\n"
            "- After each guess, you'll get feedback:\n"
            "  🟩 = Correct letter, correct position\n"
            "  🟨 = Correct letter, wrong position\n"
            "  ⬛ = Wrong letter\n"
            "- Use /wordle [your_guess] to play.\n"
            "- Your guesses are private and only visible to you.\n"
            "Good luck!"
        )
        await ctx.respond(rules)

    @commands.slash_command(
        name="wordlescoreboard", description="Display the top Wordle players"
    )
    async def wordle_scoreboard(self, ctx: discord.ApplicationContext):
        """Displays a scoreboard based on guesses"""
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        top_10 = sorted_scores[:10]
        embed = discord.Embed(title="Wordle Scoreboard", color=discord.Color.gold())
        for rank, (user_id, score) in enumerate(top_10, start=1):
            user = await self.bot.fetch_user(user_id)
            embed.add_field(
                name=f"#{rank} {user.name}", value=f"Score: {score}", inline=False
            )

        await ctx.respond(embed=embed)

    @commands.slash_command(name="wordlerestart", description="restart the word")
    async def restart(self, ctx: discord.ApplicationContext):
        """Resets the word (Only owner can for now)"""
        self.game.new_word()
        print("new word is", self.game.guess_word)
        await ctx.respond("new word set")
