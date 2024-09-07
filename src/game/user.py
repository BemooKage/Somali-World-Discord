# Models

class User:
    """User for wordle"""
    def __init__(self, user_id: int, server_id: int, name: str, score=0, streak=0):
        self.id = user_id
        self.server_id = server_id
        self.name = name
        self.score = score
        self.streak = streak

    @classmethod
    def get_or_create(cls, conn, user_id: int, server_id: int, name: str = 'unknown'):
        """Get or create new users"""
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=? AND server_id=?", (user_id,server_id,))
        user_data = c.fetchone()
        if user_data:
            user = cls(*user_data)
        else:
            user = cls(user_id, server_id, name)
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (user.id, user.server_id, user.name, user.score, user.streak))
        conn.commit()
        return user

    def save(self, conn):
        c = conn.cursor()
        c.execute("UPDATE users SET server_id=?, name=?, score=?, streak=? WHERE id=?",
                  (self.server_id, self.name, self.score, self.streak, self.id))
        conn.commit()
