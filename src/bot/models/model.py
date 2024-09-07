"""Models used throughout the Wordle game"""


from dataclasses import dataclass


@dataclass
class Guess:
    """Guess for given word"""


@dataclass
class UserGuess:
    """Associated Guess for given word for user"""
    user_id: int
    word_id: int
    answered: bool = False
