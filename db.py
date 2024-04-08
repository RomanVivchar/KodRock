import psycopg2


class Database:
    def __init__(self, database, user, password, host, port):
        self.connection = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        self.cursor = self.connection.cursor()

    def add_user(self, telegram_id: str):
        with self.connection:
            return self.cursor.execute("INSERT INTO user (telegram_id) VALUES (?)", (telegram_id,))

    def user_exists(self, telegram_id: str):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM user WHERE telegram_id = ?", (telegram_id,)).fetchall()
            return bool(len(result))

    def set_name(self, telegram_id: str, name: str):
        with self.connection:
            return self.cursor.execute("UPDATE user SET name = ? WHERE telegram_id = ?", (name, telegram_id,))

    def set_last_name(self, telegram_id: str, last_name: str):
        with self.connection:
            return self.cursor.execute("UPDATE user SET last_name = ? WHERE telegram_id = ?", (last_name, telegram_id,))

    def set_email(self, telegram_id: str, email: str):
        with self.connection:
            return self.cursor.execute("UPDATE user SET email = ? WHERE telegram_id = ?"), (email, telegram_id,)

    def set_phone(self, telegram_id: str, phone: str):
        with self.connection:
            return self.cursor.execute("UPDATE user SET phone_number = ? WHERE telegram_id = ?"), (phone, telegram_id,)

