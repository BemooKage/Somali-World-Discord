"""User Repository"""

import os
import sqlite3
from typing import List
from .user import User


class UserRepository:
    """Repository for handling user database operations."""

    def __init__(self):
        env = os.getenv("ENVIRONMENT")
        if env == "testing":
            self.conn = sqlite3.connect(":memory:")
        else:
            self.conn = sqlite3.connect("./src/data/wordle.db")
        self.create_table_if_nonexistent()

    def get_all_users_sorted(self, server_id: int) -> List[User]:
        """Get all users ordered by score"""
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM users WHERE server_id = {server_id} ORDER BY score")
        users = c.fetchall()
        return users

    def get_top_n_users_by_score(self, n: int, server_id: int) -> List[User]:
        """Returns top N users by their scores, breaking ties by streak."""
        c = self.conn.cursor()

        # Order by score descending, and break ties with streak descending
        c.execute(f"SELECT * FROM users WHERE server_id = {server_id} ORDER BY score DESC, streak DESC LIMIT {n}")

        users = [User(*u) for u in c.fetchall()]
        return users

    def create_table_if_nonexistent(self):
        """Creates table if not existent"""
        c = self.conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, server_id INTEGER NOT NULL, name TEXT NOT NULL, score INTEGER NOT NULL, streak INTEGER NOT NULL)"""
        )
        self.conn.commit()

    def get_or_create(self, user_id: int, server_id: int, name: str = "unknown") -> User:
        """Get or create a new user in the database."""
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user_data = c.fetchone()

        if user_data:
            return User(*user_data)
        else:
            new_user = User(user_id, server_id, name)
            c.execute(
                "INSERT INTO users (id, server_id, name, score, streak) VALUES (?, ?, ?, ?, ?)",
                (new_user.id, new_user.server_id, new_user.name, new_user.score, new_user.streak),
            )
            self.conn.commit()
            return new_user

    def save(self, user: User):
        """Save user data to the database."""
        c = self.conn.cursor()
        c.execute(
            "UPDATE users SET server_id=?, name=?, score=?, streak=? WHERE id=?",
            (user.server_id, user.name, user.score, user.streak, user.id),
        )
        self.conn.commit()
