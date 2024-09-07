# """Word database"""


# import datetime
# import sqlite3


# class Word:
#     """Words used for SomaliWordle"""
#     def __init__(self, word_id: int, word: str, last_used=None, times_used=0):
#         self.id = word_id
#         self.word = word
#         self.last_used = last_used
#         self.times_used = times_used
#         self.guesses = 0

#     @classmethod
#     def get_random(cls):
#         conn = sqlite3.connect('wordle.db')
#         c = conn.cursor()
#         # Get words not used in the last 30 days, prioritize less used words
#         c.execute("SELECT * FROM words WHERE last_used IS NULL OR last_used < date('now', '-30 days') ORDER BY times_used, RANDOM() LIMIT 1")
#         word_data = c.fetchone()
#         if word_data:
#             word = cls(*word_data)
#             word.update_usage()
#         else:
#             # If no word found, reset all words and pick a random one
#             c.execute("UPDATE words SET last_used = NULL")
#             c.execute("SELECT * FROM words ORDER BY RANDOM() LIMIT 1")
#             word_data = c.fetchone()
#             word = cls(*word_data)
#             word.update_usage()
#         conn.close()
#         return word
    
#     def add_guesses

#     def update_usage(self):
#         """Update wordle"""
#         conn = sqlite3.connect('wordle.db')
#         c = conn.cursor()
#         self.last_used = datetime.now().date()
#         self.times_used += 1
#         c.execute("UPDATE words SET last_used=?, times_used=? WHERE id=?", 
#                   (self.last_used, self.times_used, self.id))
#         conn.commit()
#         conn.close()