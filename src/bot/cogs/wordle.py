"""Discord Cog for Wordle game"""

import asyncio
from collections import defaultdict
import datetime
import random
from typing import List

import discord
from discord.ext import commands, tasks

from game.wordle_game import GuessResult, WordleGame
from bot.views.wordle_messages import (
    correct_guess_message,
    create_guess_visual,
    create_scoreboard,
    guess_message,
    incorrect_guess_message,
    invalid_word_message,
    max_retries_message,
)
from game.users import UserRepository
from game.user import User
from utils.autocompletes import word_autocompletes


class WordleCog(discord.Cog):
    """Main Cog for Wordle GAme"""

    def __init__(self, bot):
        self.bot = bot
        self.word_manager = bot.word_game
        self.game = WordleGame(self.word_manager)
        self.scores = defaultdict(int)
        self.streaks = {}
        self.guesses = {}
        self.user_repo = UserRepository()
        self.change_word.start()

    def cog_unload(self):
        self.change_word.cancel()

    # @tasks.loop(time=datetime.time(hour=0, minute=0))  # Run daily at midnight
    @tasks.loop(hours=3)
    async def change_word(self):
        """Changes the word ever x time"""
        old_word = self.game.guess_word
        self.game.reset_game()
        print(f"New word set: {self.game.guess_word}")
        await self.send_new_word_message(old_word)
        await self.handle_current_guesses()

    async def handle_current_guesses(self):
        """Removes all guesses from users not completed and autoset their scores"""
        for user_id, guesses in self.game.guesses.items():
            if len(guesses) > 0 and guesses[-1] != self.game.guess_word:
                user = await self.bot.fetch_user(user_id)
                await user.send(
                    f"The word has changed. The correct word was {self.game.guess_word}."
                )

    async def send_new_word_message(self, old_word: str):
        """Sends new word notification to all servers"""
        await self.bot.new_word_notification(old_word=old_word)

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
        server_id = ctx.guild.id
        guess_result = self.game.guess(
            user_id=ctx.author.id, server_id=server_id, name=ctx.author.name, word_guess=guess
        )
        user = self.user_repo.get_or_create(
            user_id=ctx.author.id, server_id=server_id, name=ctx.author.name
        )
        attempts = self.game.guesses[server_id][user.id].attempts()
        if guess_result == GuessResult.CORRECT:
            embed = correct_guess_message(ctx=ctx, user=user, attempts=attempts)
            return await ctx.respond(embed=embed)
        elif guess_result == GuessResult.FAILED:
            embed = incorrect_guess_message(
                ctx=ctx, user=user, word=self.game.guess_word
            )
            return await ctx.respond(embed=embed, ephemeral=True)
        elif guess_result == GuessResult.INCORRECT:
            guessed_word = self.game.guesses[server_id][user.id].last_guess()
            visual = create_guess_visual(
                guess=guessed_word, correct_word=self.game.guess_word
            )
            embed = guess_message(ctx=ctx, user=user, visual=visual, attempts=attempts)
            return await ctx.respond(embed=embed, ephemeral=True)
        elif guess_result == GuessResult.MAX_ATTEMPTS:
            embed = max_retries_message(
                ctx=ctx, user=user, correct_word=self.game.guess_word
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        if (
            guess_result == GuessResult.INVALID_WORD
            or guess_result == GuessResult.UNKNOWN_WORD
        ):
            embed = invalid_word_message(ctx=ctx, user=user, guess_word=guess)
            return await ctx.respond(embed=embed, ephemeral=True)

        raise Exception("Something went wrong 🫢")

    def calculate_score(self, server_id: int, user_id: int):
        """Calculates the score for given user for display"""
        attempts = len(self.game.guesses[server_id][user_id])
        score = max(7 - attempts, 1)  # 6 points for 1 attempt, 1 point for 6 attempts
        self.scores[user_id] += score

        self.scores[user_id] = self.scores.get(user_id, 0) + score
        # if self.streaks[user_id] > 0:
        # self.streaks[user_id] +=

    @commands.slash_command(
        name="wordlehint", description="Get a hint for the current word"
    )
    async def wordle_hint(self, ctx: discord.ApplicationContext):
        hint = self.word_manager.get_hint(self.game.guess_word)
        await ctx.respond(f"Hint: {hint}", ephemeral=True)

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
        """Displays scoreboard"""
        users: List[User] = self.user_repo.get_top_n_users_by_score(
            n=10, server_id=ctx.guild.id
        )
        embed = await create_scoreboard(users=users)

        await ctx.respond(embed=embed)

    @commands.slash_command(name="revealword", description="revealing the word")
    async def reveal_word(self, ctx):
        """Reveal the word"""
        word = self.game.guess_word
        embed = discord.Embed(title="Revealing the Wordle", color=discord.Color.gold())
        message = await ctx.respond(embed=embed)
        for i in range(len(word)):
            embed.description = f"The word is: {'_' * (len(word) - i) + word[:i]}"
            await message.edit(embed=embed)
            await asyncio.sleep(1)
        embed.description = f"The word is: {word}"
        await message.edit(embed=embed)

    @commands.slash_command(name="wordlerestart", description="restart the word")
    @commands.has_permissions(administrator=True)
    async def restart(self, ctx: discord.ApplicationContext):
        """Resets the word (Only owner can for now)"""
        self.game.new_word()
        print("new word is", self.game.guess_word)
        await ctx.respond("new word set")

    @play_wordle.error
    async def play_wordle_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.respond(
                "Please provide a guess. Usage: /wordle [your_guess]", ephemeral=True
            )
        elif isinstance(error, Exception):
            await ctx.respond("Something went wrong ...", ephemeral=True)
