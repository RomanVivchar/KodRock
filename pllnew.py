import psycopg
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, ApplicationBuilder, filters, CommandHandler, MessageHandler, ContextTypes, \
    ConversationHandler, CallbackContext, \
    CallbackQueryHandler
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


app = ApplicationBuilder().token("7188985096:AAFn7ijrux_O4JAEkJQWeAk3J8V8fg_wJrk").build()


conn = psycopg.connect(dbname="project", user="bot", password="bot123", host="194.87.239.80", port="5432")
cur = conn.cursor()

async def send_message(bot, user_id, message):
    await bot.send_message(chat_id=user_id, text=message)
    while True:
        cur.execute("""
          SELECT answer_id, question_id
            FROM answer
           WHERE NOT is_sent
             FOR UPDATE SKIP LOCKED
           LIMIT 1
      """)

        for (answer_id, question_id,) in cur:
            cur.execute("""
              SELECT user_id
                FROM question
               WHERE question_id = %s
          """, (question_id,))

            user_id = cur.fetchone()

            await context.bot.send_message(chat_id=user_id, text=text)

            cur.execute("""
          UPDATE answer
             SET is_sent = true
           WHERE answer_id = %s
        """, (answer_id,))


def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    text = "Hello! This is a test message."
    asyncio.run(send_message(updater.bot, user_id, text))


def main():
    app.add_handler(CommandHandler("start", start)),

    app.run_polling()
    app.idle()


if __name__ == '__main__':
    main()
