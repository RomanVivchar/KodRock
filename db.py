import psycopg2
import datetime


class Database:
    def __init__(self, database, user, password, host, port):
        self.connection = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        self.cursor = self.connection.cursor()

    def add_user(self, telegram_id: int):
        with self.connection:
            return self.cursor.execute("INSERT INTO public.user (user_id) VALUES (%s)", (telegram_id,))

    def user_exists(self, telegram_id: int):
        with self.connection:
            self.cursor.execute("SELECT * FROM public.user WHERE user_id = (%s)", (telegram_id,))
            row = self.cursor.fetchall()
            return bool(len(row))

    def set_name(self, telegram_id: int, name: str):
        with self.connection:
            return self.cursor.execute("UPDATE public.user SET name = (%s) WHERE user_id = (%s)",
                                       (name, telegram_id,))

    def set_last_name(self, telegram_id: int, last_name: str):
        with self.connection:
            return self.cursor.execute("UPDATE public.user SET last_name = (%s) WHERE user_id = (%s)",
                                       (last_name, telegram_id,))

    def set_email(self, telegram_id: int, email):
        with self.connection:
            query = "UPDATE public.user SET email = (%s) WHERE user_id = (%s)"
            data = (email, telegram_id,)
            return self.cursor.execute(query, data)

    def set_phone(self, telegram_id: int, phone):
        with self.connection:
            query = "UPDATE public.user SET phone_number = (%s) WHERE user_id = (%s)"
            data = (phone, telegram_id,)
            return self.cursor.execute(query, data)

    def add_question(self, telegram_id: int, question: str):
        with self.connection:
            return self.cursor.execute("INSERT INTO public.question (user_id, text, date) VALUES (%s, %s, %s)",
                                       (telegram_id, question, datetime.datetime.now()))

    def add_tags(self, telegram_id: int, tags: str):
        with self.connection:
            return self.cursor.execute("UPDATE public.question SET tag = (%s) WHERE user_id = (%s)",
                                       (tags, telegram_id,))

    def all_questions(self) -> list[tuple]:
        with self.connection:
            self.cursor.execute("SELECT question_id, text, date, user_id FROM public.question ORDER BY date DESC")
            rows = self.cursor.fetchall()

            return rows

    def get_question(self, question_id: int) -> tuple:
        with self.connection:
            self.cursor.execute("SELECT text, date_trunc('minute', date)::TIMESTAMP, user_id "
                                "FROM question WHERE question_id = (%s)", (question_id,))
            row = self.cursor.fetchone()
            return row

    def get_user(self, telegram_id: int):
        with self.connection:
            self.cursor.execute("SELECT last_name, name FROM public.user WHERE user_id = (%s)", (telegram_id,))
            row = self.cursor.fetchone()
            return row

    def all_answers(self, question_id: int) -> list[tuple]:
        with self.connection:
            self.cursor.execute("SELECT answer_id, text, date_trunc('minute', date)::TIMESTAMP, user_id "
                                "FROM answer "
                                "WHERE question_id = (%s)"
                                "ORDER BY date DESC", (question_id,))
            rows = self.cursor.fetchall()

            return rows

    def add_answer(self, telegram_id: int, answer: str, question_id: int):
        with self.connection:
            return self.cursor.execute("INSERT INTO answer (text, user_id, date, question_id) VALUES (%s, %s, %s, %s)",
                                       (answer, telegram_id, datetime.datetime.now(), question_id))
