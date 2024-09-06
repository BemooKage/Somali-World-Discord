"""Loguru configurations"""

from loguru import logger
import os


# Centralized logging configuration
def configure_logging():
    """Centralized logging configuration"""
    # Ensure the log directory exists
    log_directory = "data/logs"
    os.makedirs(log_directory, exist_ok=True)

    # Remove the default logger to avoid duplicating logs
    logger.remove()

    # Logger for general events
    logger.add(
        f"{log_directory}/general.log",
        filter=lambda record: record["extra"].get("type") == "general",
        level="INFO",
    )

    # Logger for join events
    logger.add(
        f"{log_directory}/join_info.log",
        filter=lambda record: record["extra"].get("type") == "join",
        level="INFO",
    )

    # Logger for wordle game guesses
    logger.add(
        f"{log_directory}/wordle_guesses.log",
        filter=lambda record: record["extra"].get("type") == "wordle_guess",
        level="INFO",
    )


# Call this to set up loggers when the bot starts
configure_logging()
