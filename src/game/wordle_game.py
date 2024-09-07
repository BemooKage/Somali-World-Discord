"""WordleGame"""
from enum import Enum, auto
from typing import Dict, List

from .users import UserRepository
from .word_manager import WordleManager
from .user import User


class GuessResult(Enum):
    """The game states"""

    CORRECT = auto()
    MAX_ATTEMPTS = auto()
    FAILED = auto()
    INCORRECT = auto()
    UNKNOWN_WORD = auto()
    INVALID_WORD = auto()


class UserGuess:
    """Holds data for guesses of wordle for current word"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.guesses = []
        self.completed = False

    def remaining_attempts(self) -> int:
        """Remaining attempts for user guesses"""
        if self.completed:
            return 0

        return 6 - len(self.guesses)

    def finished(self) -> bool:
        """Returns if user guesses are done"""
        return self.completed or self.remaining_attempts() == 0

    def attempts(self) -> int:
        """Gets current attempt count"""
        return len(self.guesses)
    
    def last_guess(self) -> str:
        """Returns last guessed word"""
        return self.guesses[-1]



class WordleGame:
    """Base Wordle Game (unassociated to discord)"""

    def __init__(self, word_manager: WordleManager):
        self.word_manager = word_manager
        self.user_repo = UserRepository()
        self.guess_word = ""
        self.guesses: Dict[int, Dict[int, UserGuess]] = {}
        self.max_attempts = 6
        self.new_word()
        self.attempt_weight = {1: 10, 2: 7, 3: 5, 4: 3, 5: 2, 6: 1}

    def new_word(self):
        """Gets new word from word manager"""
        self.guess_word = self.word_manager.get_random_word()
        print("word is", self.guess_word)

    def is_valid(self, word):
        """Is word valid"""
        return self.word_manager.is_valid_word(word=word)

    def calculate_final_score(self, user_id):
        """Calculates user score"""

    def reset_game(self):
        """Resets the game"""
        self.guess_word = ""
        self.guesses = {}
        self.new_word()

    def add_user_guess(self, user_id: int, server_id: int, guess: str):
        """Adds new guess to user guess"""
        self.guesses[server_id][user_id].guesses.append(guess)

    def guess(self, user_id: int, server_id: int, name: str, word_guess: str) -> GuessResult:
        """Sets new guess"""
        user = self.user_repo.get_or_create(user_id=user_id, server_id=server_id, name=name)

        # process user input
        word_guess = word_guess.lower().strip()

        # Validate user action for guess is valid
        is_invalid = self.validate_action(guess_word=word_guess, user_id=user_id, server_id=server_id)
        if is_invalid:
            return is_invalid

        # Add user if not already existing in guess table
        if server_id not in self.guesses:
            self.guesses[server_id] = {}
        
        if user_id not in self.guesses[server_id]:
            self.guesses[server_id][user_id] = UserGuess(user_id=user_id)

        if not self.word_manager.is_valid_word(word_guess):
            return GuessResult.UNKNOWN_WORD

        if len(word_guess) != 5:
            return GuessResult.INVALID_WORD

        self.add_user_guess(user_id=user_id,server_id=server_id, guess=word_guess)

        result: GuessResult = None

        if word_guess == self.guess_word:
            self.guesses[server_id][user_id].completed = True
            self.gain_score(user=user)
            user.streak += 1
            result = GuessResult.CORRECT
        elif self.guesses[server_id][user_id].finished():
            user.streak = 0
            self.lose_score(user=user)
            result = GuessResult.FAILED
        else:
            result = GuessResult.INCORRECT

        self.user_repo.save(user)
        return result

    def gain_score(self, user: User):
        """Calculates the gain from correct guess"""
        attempt_number = self.guesses[user.server_id][user.id].attempts()

        if attempt_number > len(self.attempt_weight):
            attempt_number = len(self.attempt_weight)

        gained_score = self.attempt_weight[attempt_number]

        streak_bonus = user.streak * 2
        total_score = gained_score + streak_bonus
        print('gained score', total_score)
        user.score += total_score

    def lose_score(self, user: User):
        """Penalise the user for incorrect guesses"""
        attempt_number = self.guesses[user.server_id][user.id].attempts()

        penalty = min(attempt_number, 5)
        user.score = max(user.score - penalty, 0)

    def validate_action(self, guess_word: str, user_id: int, server_id: int) -> GuessResult:
        """Validates the guess word"""

        if server_id not in self.guesses:
            self.guesses[server_id] = {}
        if user_id not in self.guesses[server_id]:
            self.guesses[server_id][user_id] = UserGuess(user_id=user_id)

        if not self.word_manager.is_valid_word(guess_word):
            return GuessResult.UNKNOWN_WORD

        if len(guess_word) != 5:
            return GuessResult.INVALID_WORD

        if self.guesses[server_id][user_id].finished():
            return GuessResult.MAX_ATTEMPTS
        return None
