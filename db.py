import psycopg2


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
            return self.cursor.execute("UPDATE public.user SET name = (%s) WHERE user_id = (%s)", (name, telegram_id,))

    def set_last_name(self, telegram_id: int, last_name: str):
        with self.connection:
            return self.cursor.execute("UPDATE public.user SET last_name = (%s) WHERE user_id = (%s)", (last_name, telegram_id,))

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

