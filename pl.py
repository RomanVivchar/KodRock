import psycopg2
import asyncio
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, ApplicationBuilder

conn = psycopg2.connect(dbname="project", user="bot", password="bot123", host="194.87.239.80", port="5432")
cur = conn.cursor()

app = ApplicationBuilder().token("7188985096:AAFn7ijrux_O4JAEkJQWeAk3J8V8fg_wJrk").build()


async def send_message(bot, user_id, message):
    await bot.send_message(chat_id=user_id, text=message)


async def send_question(update: Update, context: CallbackContext):
    cur.execute("SELECT * FROM question_id WHERE new = True;")
    new_requests = cur.fetchall()

    for request in new_requests:
        user_id = request[0]
        message = f"🔔 Новый запрос на знание: {request[1]}\n{request[2]}"
        await send_message(context.bot, user_id, message)


def notify_question(update: Update, context: CallbackContext):
    asyncio.run(send_question(update, context))


app.add_handler(CommandHandler("notify_question", notify_question))


async def start_periodic_updates():
    while True:
        await asyncio.sleep(24 * 60 * 60)
        notify_question()


def main():
    app.run_polling()


if __name__ == '__main__':
    main()
