import psycopg2
import datetime


class Database:
    def __init__(self, database, user, password, host, port):
        self.connection = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        self.cursor = self.connection.cursor()

    def add_user(self, telegram_id: int):
        with self.connection:
            return self.cursor.execute("INSERT INTO users (user_id) VALUES (%s)", (telegram_id,))

    def user_exists(self, telegram_id: int):
        with self.connection:
            self.cursor.execute("SELECT * FROM users WHERE user_id = (%s)", (telegram_id,))
            row = self.cursor.fetchall()
            if len(row) < 2:
                return False
            return True

    def set_name(self, telegram_id: int, name: str):
        with self.connection:
            return self.cursor.execute("UPDATE users SET name = (%s) WHERE user_id = (%s)",
                                       (name, telegram_id,))

    def set_last_name(self, telegram_id: int, last_name: str):
        with self.connection:
            return self.cursor.execute("UPDATE users SET last_name = (%s) WHERE user_id = (%s)",
                                       (last_name, telegram_id,))

    def set_email(self, telegram_id: int, email):
        with self.connection:
            query = "UPDATE users SET email = (%s) WHERE user_id = (%s)"
            data = (email, telegram_id,)
            return self.cursor.execute(query, data)

    def set_phone(self, telegram_id: int, phone):
        with self.connection:
            query = "UPDATE users SET phone_number = (%s) WHERE user_id = (%s)"
            data = (phone, telegram_id,)
            return self.cursor.execute(query, data)

    def add_question(self, telegram_id: int, question: str):
        with self.connection:
            return self.cursor.execute("INSERT INTO question (user_id, text, date) VALUES (%s, %s, %s)",
                                       (telegram_id, question, datetime.datetime.now()))

    def add_tags(self, telegram_id: int, tags: str):
        with self.connection:
            return self.cursor.execute("UPDATE question SET tag = (%s) WHERE user_id = (%s)",
                                       (tags, telegram_id,))

    def all_questions(self) -> list[tuple]:
        with self.connection:
            self.cursor.execute("SELECT question_id, text, date, user_id "
                                "FROM question ORDER BY date DESC")
            rows = self.cursor.fetchall()

            return rows

    def get_question(self, question_id: int) -> tuple:
        with self.connection:
            self.cursor.execute("SELECT text, date, user_id "
                                "FROM question WHERE question_id = (%s)", (question_id,))
            row = self.cursor.fetchone()
            return row

    def get_user(self, telegram_id: int):
        with self.connection:
            self.cursor.execute("SELECT last_name, name FROM users WHERE user_id = (%s)", (telegram_id,))
            row = self.cursor.fetchone()
            return row

    def all_users(self) -> list[tuple]:
        with self.connection:
            self.cursor.execute("with count_questions as ("
                                "SELECT user_id, COUNT(user_id) as total FROM question GROUP BY user_id), "
                                "count_answers as ("
                                "SELECT user_id, COUNT(user_id) as total FROM answer GROUP BY user_id)"
                                "SELECT last_name, name, phone_number, email, "
                                "COALESCE(count_answers.total, 0) as answers, "
                                "COALESCE(count_questions.total, 0) as questions "
                                "FROM users "
                                "LEFT JOIN count_questions ON users.user_id = count_questions.user_id "
                                "LEFT JOIN count_answers ON users.user_id = count_answers.user_id "
                                "ORDER BY answers DESC, questions DESC")
            rows = self.cursor.fetchall()

            return rows

    def all_answers(self, question_id: int) -> list[tuple]:
        with self.connection:
            self.cursor.execute("SELECT answer_id, text, date, user_id "
                                "FROM answer "
                                "WHERE question_id = (%s)"
                                "ORDER BY date DESC", (question_id,))
            rows = self.cursor.fetchall()

            return rows

    def add_answer(self, telegram_id: int, answer: str, question_id: int):
        with self.connection:
            return self.cursor.execute("INSERT INTO answer (text, user_id, date, question_id) VALUES (%s, %s, %s, %s)",
                                       (answer, telegram_id, datetime.datetime.now(), question_id))

    def check_strike(self, telegram_id: int):
        with self.connection:
            self.cursor.execute("SELECT COUNT(*) FROM answer WHERE date = (%s) AND user_id = (%s)",
                                (datetime.datetime.now().date(), telegram_id))
            row = self.cursor.fetchone()

            return row

    def insert_gems(self, telegram_id: int, gems: int, quantity_gems=0):
        with self.connection:
            return self.cursor.execute("UPDATE users SET gems = (%s) WHERE user_id = (%s)",
                                       (gems + quantity_gems, telegram_id,))

    def get_gems(self, telegram_id: int):
        with self.connection:
            self.cursor.execute("SELECT gems FROM users WHERE user_id = (%s)", (telegram_id,))
            row = self.cursor.fetchone()

            return row

    def account(self, telegram_id: int):
        with self.connection:
            self.cursor.execute("SELECT last_name, name, phone_number, email, gems"
                                " FROM users WHERE user_id = (%s)", (telegram_id,))
            row = self.cursor.fetchone()

            return row

    def my_answers(self, telegram_id: int):
        with self.connection:
            self.cursor.execute("SELECT answer_id, text, date, question_id "
                                "FROM answer "
                                "WHERE user_id = (%s) "
                                "ORDER BY date DESC", (telegram_id,))
            rows = self.cursor.fetchall()

            return rows

    def update_answer(self, answer: str, answer_id: int):
        with self.connection:
            return self.cursor.execute("UPDATE answer SET text = (%s) WHERE answer_id = (%s)",
                                       (answer, answer_id,))

    def my_questions(self, telegram_id: int):
        with self.connection:
            self.cursor.execute("SELECT question_id, text, date FROM question WHERE user_id = (%s)", (telegram_id,))
            rows = self.cursor.fetchall()
            return rows

    def update_question(self, question: str, question_id: int):
        with self.connection:
            return self.cursor.execute("UPDATE question SET text = (%s)  WHERE question_id = (%s)",
                                       (question, question_id,))
