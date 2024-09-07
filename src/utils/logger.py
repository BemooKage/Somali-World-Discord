"""Logging code"""
from loguru import logger

from utils.log_config import configure_logging

def log_event(event_type, message, **kwargs):
    """Log event (basic)"""
    logger.bind(type=event_type).info(message, **kwargs)

def log_join_event(user_id):
    """Logs events"""
    log_event("join", f"User {user_id} joined the server.")

def log_wordle_guess(user_id, guess):
    """Logs wordle guesses"""
    log_event("wordle_guess", f"User {user_id} guessed '{guess}' in Wordle.")

def log_general_event(event_description):
    """Logs general events"""
    log_event("general", event_description)

configure_logging()