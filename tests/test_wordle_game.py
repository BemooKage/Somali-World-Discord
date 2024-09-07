import pytest
from src.game.wordle_game import WordleGame, GuessResult
from src.game.user import User
from src.game.users import UserRepository
from src.game.word_manager import WordleManager


@pytest.fixture
def set_testing_environment(monkeypatch):
    """Set environment to 'testing'."""
    monkeypatch.setenv("ENVIRONMENT", "testing")


@pytest.fixture
def word_manager():
    """Fixture to provide a real WordleManager."""
    return WordleManager()


@pytest.fixture
def user_repo(set_testing_environment):
    """Fixture to provide a UserRepository for testing (in-memory)."""
    return UserRepository()


@pytest.fixture
def wordle_game(word_manager, set_testing_environment):
    """Fixture to provide a WordleGame instance."""
    return WordleGame(word_manager=word_manager)


@pytest.fixture
def mock_user():
    """Fixture to create a mock User."""
    return User(user_id=1, name="test_user")


def test_new_word(wordle_game):
    """Test if the game sets a new word on start."""
    wordle_game.new_word()
    assert len(wordle_game.guess_word) == 5  # Assuming all words are 5 letters


def test_guess_correct(wordle_game, mock_user):
    """Test a correct guess."""
    wordle_game.new_word()
    correct_word = wordle_game.guess_word

    result = wordle_game.guess(user_id=1, name="test_user", word_guess=correct_word)

    assert result == GuessResult.CORRECT
    assert wordle_game.guesses[1].completed is True


def test_guess_incorrect(wordle_game, mock_user):
    """Test an incorrect guess."""
    wordle_game.new_word()

    random_word = get_incorrect_valid_word(game=wordle_game)

    result = wordle_game.guess(user_id=1, name="test_user", word_guess=random_word)

    assert result == GuessResult.INCORRECT
    assert not wordle_game.guesses[1].completed


def test_guess_unknown_word(wordle_game, mock_user):
    """Test guessing an unknown word."""
    wordle_game.new_word()

    result = wordle_game.guess(user_id=1, name="test_user", word_guess="wrongword")

    assert result == GuessResult.UNKNOWN_WORD
    assert not wordle_game.guesses

def test_max_attempts(wordle_game, mock_user):
    """continously guesses until reaching max count"""
    guess = get_incorrect_valid_word(game=wordle_game)

    for _ in range(wordle_game.max_attempts):
        wordle_game.guess(user_id=1, name='test_user', word_guess=guess)

    result = wordle_game.guess(user_id=1, name='test_user', word_guess=guess)
    assert result == GuessResult.MAX_ATTEMPTS

    new_user_result = wordle_game.guess(user_id=12, name='test_user', word_guess=guess)
    assert new_user_result == GuessResult.INCORRECT

def test_score_calculation(wordle_game):
    """Test if the score calculation works based on attempts."""
    wordle_game.new_word()
    word = wordle_game.guess_word

    # First attempt win
    wordle_game.guess(user_id=12, name='random', word_guess=word)
    user = wordle_game.user_repo.get_or_create(12)
    assert user.score == 10  # Score should be 10 for 1st attempt

def test_score_reduction_on_loss(wordle_game, mock_user):
    """Test if the score is reduced when the user loses."""
    wordle_game.new_word()
    guess = get_incorrect_valid_word(game=wordle_game)
    
    for _ in range(6):
        wordle_game.guess(user_id=1, name=mock_user.name, word_guess=guess)

    assert mock_user.streak == 0  # Streak should be reset on loss
    assert mock_user.score == 0    # Assuming 0 score reduction for losing

def test_multiple_user_support(wordle_game):
    """Test if the game can handle multiple users guessing independently."""
    wordle_game.new_word()
    guess = get_incorrect_valid_word(game=wordle_game)

    # User 1 guesses
    wordle_game.guess(user_id=1, name="user1", word_guess=guess)
    assert not wordle_game.guesses[1].completed

    # User 2 guesses correctly
    result = wordle_game.guess(user_id=2, name="user2", word_guess=wordle_game.guess_word)
    assert result == GuessResult.CORRECT
    assert wordle_game.guesses[2].completed

    # Ensure User 1's game state is unchanged
    assert not wordle_game.guesses[1].completed


def test_game_reset(wordle_game):
    """Test if the game can reset properly between rounds."""
    wordle_game.new_word()
    old_guess_word = wordle_game.guess_word
    wordle_game.guess(user_id=1, name="test_user", word_guess=old_guess_word)
    assert wordle_game.guesses[1].completed

    # Reset the game and ensure previous guesses are cleared
    wordle_game.reset_game()
    assert len(wordle_game.guesses) == 0  # No guesses should remain
    assert wordle_game.guess_word != old_guess_word  # New word should be generated

def get_incorrect_valid_word(game):
    """Gets a word that is not the guess word"""
    random_word = "apple"
    while (
        not game.is_valid(random_word) and random_word != game.guess_word
    ):
        random_word = game.word_manager.get_random_word()
    return random_word