"""WordleGame"""
from game.word_manager import WordleManager


class WordleGame:
    """Base Wordle Game (unassociated to discord)"""
    def __init__(self, word_manager: WordleManager):
        self.word_manager = word_manager
        self.guess_word = ""
        self.guesses = {}
        self.max_attempts = 6
        self.new_word()

    def new_word(self):
        """Gets new word from word manager"""
        self.guess_word = self.word_manager.get_random_word()
        print('word is', self.guess_word)

    def reset_guesses(self):
        """resets the guesses"""
        self.guesses = {}

    def guess(self, user_id, guess):
        """Sets new guess"""
        if user_id not in self.guesses:
            self.guesses[user_id] = []

        if len(self.guesses[user_id]) >= self.max_attempts:
            return "You've used all your attempts for today!", False

        guess = guess.lower()

        if len(guess) != 5:
            return "Please enter a 5-letter word.", False

        if not self.word_manager.is_valid_word(guess):
            return "Not a valid word. Please try again.", False

        result = []
        for i, letter in enumerate(guess):
            if letter == self.guess_word[i]:
                result.append("🟩")
            elif letter in self.guess_word:
                result.append("🟨")
            else:
                result.append("⬛")

        self.guesses[user_id].append(guess)

        if guess == self.guess_word:
            self.new_word()
            return (
                f"Correct! The word was {self.guess_word}. You guessed it in {len(self.guesses[user_id])} attempts.",
                True,
            )
        elif len(self.guesses[user_id]) == self.max_attempts:
            self.new_word()
            return (
                f"Game over! The word was {self.guess_word}. Better luck tomorrow!",
                False,
            )
        else:
            return (
                f"{''.join(result)} | {6 - len(self.guesses[user_id])} attempts remaining.",
                False,
            )
