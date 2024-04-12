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

    def add_question(self, telegram_id: int, question: str, tag: str):
        with self.connection:
            return self.cursor.execute("INSERT INTO question (user_id, text, tag, date) VALUES (%s, %s, %s, %s)",
                                       (telegram_id, question, tag, datetime.datetime.now()))

    def all_questions(self, state=True, decline=False) -> list[tuple]:
        with self.connection:
            self.cursor.execute("SELECT tag, question_id, text, rating "
                                "FROM question WHERE is_sent = (%s) AND declined = (%s) "
                                "ORDER BY rating DESC, date DESC", (state, decline,))
            rows = self.cursor.fetchall()

            return rows

    def get_question(self, question_id: int) -> tuple:
        with self.connection:
            self.cursor.execute("SELECT tag, text, date, user_id, rating "
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
                                "SELECT user_id, COUNT(user_id) as total FROM question WHERE declined is False "
                                "GROUP BY user_id), "
                                "count_answers as ("
                                "SELECT user_id, COUNT(user_id) as total FROM answer WHERE declined is False "
                                "GROUP BY user_id)"
                                "SELECT last_name, name, phone_number, email, "
                                "COALESCE(count_answers.total, 0) as answers, "
                                "COALESCE(count_questions.total, 0) as questions "
                                "FROM users "
                                "LEFT JOIN count_questions ON users.user_id = count_questions.user_id "
                                "LEFT JOIN count_answers ON users.user_id = count_answers.user_id "
                                "ORDER BY answers DESC, questions DESC")
            rows = self.cursor.fetchall()

            return rows

    def all_answers(self, question_id: int, state=True, decline=False) -> list[tuple]:
        with self.connection:
            self.cursor.execute("SELECT answer_id, text, date, user_id "
                                "FROM answer "
                                "WHERE question_id = (%s) AND is_sent = (%s) AND declined = (%s) "
                                "ORDER BY date DESC", (question_id, state, decline))
            rows = self.cursor.fetchall()

            return rows

    def add_answer(self, telegram_id: int, answer: str, question_id: int):
        with self.connection:
            return self.cursor.execute("INSERT INTO answer (text, user_id, date, question_id) VALUES (%s, %s, %s, %s)",
                                       (answer, telegram_id, datetime.datetime.now(), question_id))

    def check_strike(self, telegram_id: int):
        with self.connection:
            self.cursor.execute("SELECT COUNT(*) FROM answer "
                                "WHERE date = (%s) AND user_id = (%s) AND declined is False",
                                (datetime.datetime.now().date(), telegram_id))
            row = self.cursor.fetchone()

            return row

    def insert_gems(self, telegram_id: int, quantity_gems=0):
        with self.connection:
            return self.cursor.execute("UPDATE users SET gems = gems + (%s) WHERE user_id = (%s)",
                                       (quantity_gems, telegram_id,))

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
                                "WHERE user_id = (%s) AND declined is false "
                                "ORDER BY date DESC", (telegram_id,))
            rows = self.cursor.fetchall()

            return rows

    def update_answer(self, answer: str, answer_id: int):
        with self.connection:
            return self.cursor.execute("UPDATE answer SET text = (%s) WHERE answer_id = (%s)",
                                       (answer, answer_id,))

    def my_questions(self, telegram_id: int):
        with self.connection:
            self.cursor.execute("SELECT question_id, text, date FROM question "
                                "WHERE user_id = (%s) AND declined is false", (telegram_id,))
            rows = self.cursor.fetchall()
            return rows

    def update_question(self, question: str, question_id: int):
        with self.connection:
            return self.cursor.execute("UPDATE question SET text = (%s)  WHERE question_id = (%s)",
                                       (question, question_id,))

    def search_by_tag(self, tag: str):
        with self.connection:
            self.cursor.execute("SELECT question_id, text, date, user_id FROM question WHERE tag = (%s)",
                                (tag,))
            rows = self.cursor.fetchall()
            return rows

    def set_question_rating(self, question_id: int, rating: int):
        with self.connection:
            return self.cursor.execute("UPDATE question SET rating = rating + (%s) WHERE question_id = (%s)",
                                       (rating + 1, question_id,))

    def check_admin(self, telegram_id: int):
        with self.connection:
            self.cursor.execute("SELECT COUNT(*) FROM admins WHERE user_id = (%s)", (telegram_id,))
            row = self.cursor.fetchone()
            return bool(len(row))

    def check_entry_admin(self, telegram_id: int, login: str, password: str):
        with self.connection:
            self.cursor.execute("SELECT user_id FROM admins "
                                "WHERE user_id = (%s) AND login = (%s) AND password = (%s)",
                                (telegram_id, login, password,))
            row = self.cursor.fetchone()
            return bool(row)

    def set_true_question(self, question_id: int, decline=False):
        with self.connection:
            return self.cursor.execute("UPDATE question SET is_sent = True, declined = (%s) WHERE question_id = (%s)",
                                       (decline, question_id,))

    def set_true_answer(self, answer_id: int, decline=False):
        with self.connection:
            return self.cursor.execute("UPDATE answer SET is_sent = True, declined = (%s) WHERE answer_id = (%s)",
                                       (decline, answer_id,))
