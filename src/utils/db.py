"""database stuff"""

# Database Setup
import sqlite3


def create_tables():
    """create the db if not created basically."""
    conn = sqlite3.connect('./src/data/wordle.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, score INTEGER, streak INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS words
                 (id INTEGER PRIMARY KEY, word TEXT, last_used DATE, times_used INTEGER)''')
    conn.commit()
    conn.close()