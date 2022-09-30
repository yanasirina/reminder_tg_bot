import sqlite3


CREATE_USER = """
INSERT INTO users (user_id, username, chat_id) VALUES (?, ?, ?);
"""

GET_USER = """
SELECT user_id, username, chat_id FROM users WHERE user_id = %s;
"""

class SQLiteClient:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.conn = None

    def create_conn(self):
        self.conn = sqlite3.connect(self.filepath, check_same_thread=False)

    def execute_command(self, command: str, params: tuple):
        if self.conn is not None:
            self.conn.execute(command, params)
            self.conn.commit()
        else:
            raise ConnectionError("Вы не создали подключение к базе данных")

    def execute_select_command(self, command: str):
        if self.conn is not None:
            cur = self.conn.cursor()
            cur.execute(command)
            return cur.fetchall()
        else:
            raise ConnectionError("Вы не создали подключение к базе данных")


sqlite_client = SQLiteClient("users.db")
sqlite_client.create_conn()
a = sqlite_client.execute_select_command(GET_USER % (1, ))
с = 1
