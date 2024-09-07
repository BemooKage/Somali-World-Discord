"""All Wordle Discord Messages"""

from dataclasses import dataclass
import os
import random
from typing import Dict, List
from discord import ApplicationContext, Bot, User, Embed, EmbedAuthor, EmbedFooter, Color
import game.user as wordle_user
from bot.models.model import UserGuess


@dataclass
class UserScore:
    user: User
    guesses: List[bool]
    score: int


def create_score_board(
    user_guesses: Dict[int, UserGuess],
    users: List[User],
):
    """Returns a full message of user scores"""
    ## Overall scores
    score_board: Dict[int, UserScore] = {}
    for user_id, user_guess in user_guesses.items():
        score_board[user_id] = UserScore(user=users[user_id], score=score)

    embed_list: List[Embed] = []
    bot_avatar = os.getenv("BOT_LOGO")
    for user_score in score_board.values():
        embed = Embed(
            author=EmbedAuthor(name=user_score.user.name, icon_url=user_score.score),
            footer=EmbedFooter(text="Somali Wordle bot", icon_url=bot_avatar),
        )


async def create_scoreboard(users: List[wordle_user.User]):
    """Scoreboard message"""
    embed = Embed(title="🏆 Wordle Leaderboard", color=Color.gold())

    leaderboard = ""
    for rank, user in enumerate(users, start=1):
        emoji = get_rank_emoji(rank)
        leaderboard += (
            f"{emoji} **{user.name}** - Score: {user.score} | Streak: {user.streak}\n"
        )

    embed.description = leaderboard

    # Add some statistics
    total_players = len(users)
    avg_score = round(sum([user.score for user in users]) / total_players, 2)
    most_streaked_users = top_in_hot_mode_players(users=users)
    embed.add_field(
        name="📊 Statistics",
        value=f"```Total Players: {total_players}\nAverage Score: {avg_score}\nTop Streaked Players:\n{most_streaked_users}```",
        inline=False,
    )

    # Add a random Wordle fact
    embed.add_field(
        name="💡 Did you know?", value=get_random_wordle_fact(), inline=False
    )

    return embed

def get_rank_emoji(rank: int):
    """Emoji trophy by current rank (index)"""
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    else:
        return f"{rank}."

def top_in_hot_mode_players(users: List[User], limit: int = 3) -> str:
    """Returns top players on a hot streak, breaking ties by score!"""
    sorted_streak_users = sorted(users, key=lambda user: (user.streak, user.score), reverse=True)
    hot_messages = []
    for rank, user in enumerate(sorted_streak_users[:limit]):
        lit = '🔥' * (limit - rank)
        hot_messages.append(f"\t{lit} - {user.name} - ({user.streak})")
    return "\n".join(hot_messages)

def get_random_wordle_fact():
    facts = [
        "Wordle was created by Welsh software engineer Josh Wardle.",
        "The game was originally made for Wardle's partner, who loves word games.",
        "Wordle was sold to The New York Times in January 2022.",
        "There are 2,315 possible solution words in Wordle.",
        "The most common starting word is reportedly 'ADIEU'.",
    ]
    return random.choice(facts)

def correct_guess_message(
    ctx: ApplicationContext, user: wordle_user.User, attempts: int
) -> Embed:
    """Returns Embed of correct guess message"""
    embed = Embed(title="Wordle Guess", color=Color.green())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
    embed.description = (
        f"🎉 Congratulations! You've guessed the word in {attempts} attempts!"
    )
    embed.set_footer(text=f"Score: {user.score} | Streak: {user.streak}")
    return embed


def incorrect_guess_message(
    ctx: ApplicationContext, user: wordle_user.User, word: str
) -> Embed:
    """Incorrect message"""
    embed = Embed(title="Wordle Guess", color=Color.red())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)

    embed.description = f"\nGame over! The word was **{word}**."

    embed.set_footer(text=f"Score: {user.score} | Streak: {user.streak}")
    return embed


def guess_message(
    ctx: ApplicationContext, user: wordle_user.User, visual: str, attempts: int
) -> Embed:
    """Creates ephermal embed for current guess"""
    embed = Embed(title="Wordle Guess", color=Color.blue())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)

    embed.add_field(name="Your Guess", value=visual, inline=False)
    embed.description = f"Not quite! You have {6 - attempts} attempts remaining."

    if attempts == 1:
        embed.set_footer(text=f"Score: {user.score} | Streak: {user.streak}")
    else:
        random_fact = get_somali_language_fact()
        embed.set_footer(text=random_fact)

    return embed

def data_facts_for_the_nerds():
    """Return random data fact for the nerds"""
    facts = [
        "The most common word length in Somali Wordle is 9, with 99,153 n-grams of this length.",
        "The most frequent n-gram in Somali Wordle is 'oo', which appears 2,124,975 times.",
        "The most common starting letter in Somali Wordle is 'd', which appears in 79,790 n-grams.",
        "The most common word ending in Somali Wordle is 'da', which appears in 48,970 n-grams.",
    ]
    
    return random.choice(facts)

def get_somali_language_fact():
    """Returns basic facts from GPT ngl"""
    facts = [
        "The Somali language is part of the Afro-Asiatic family and is spoken by over 15 million people.",
        "Somali uses the Latin alphabet, but it was standardized as the official script in 1972.",
        "Somali is known for its rich use of vowels and emphasis on vowel harmony.",
        "Many Somali words are derived from Arabic, reflecting the close cultural and linguistic ties.",
    ]
    return random.choice(facts)

def create_guess_visual(guess: str, correct_word: str) -> str:
    """Creates simple color cells for guess vs correct"""
    visual = ""
    for i, letter in enumerate(guess):
        if letter == correct_word[i]:
            visual += "🟩"  # Green for correct position
        elif letter in correct_word:
            visual += "🟨"  # Yellow for correct letter, wrong position
        else:
            visual += "⬛"  # Black for incorrect letter
    return visual


def max_retries_message(
    ctx: ApplicationContext, user: wordle_user.User, correct_word: str
) -> Embed:
    """Max retries reached message"""
    embed = Embed(title="Wordle Guess", color=Color.red())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)

    embed.description = (
        f"🚫 You've reached the maximum number of attempts!"
        f"\nThe correct word was **{correct_word}**."
    )

    embed.set_footer(text=f"Score: {user.score} | Streak: {user.streak}")
    return embed


def invalid_word_message(
    ctx: ApplicationContext, user: wordle_user.User, guess_word: str
) -> Embed:
    """Invalid word message"""
    embed = Embed(title="Wordle Guess", color=Color.red())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)

    embed.description = f"✖️ The word you guessed '{guess_word}' is not valid. Make sure it's the correct length and a real word."

    embed.set_footer(text=f"Score: {user.score} | Streak: {user.streak}")
    return embed
