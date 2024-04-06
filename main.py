import re
import sqlite3
import requests
import telegram
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters
)
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

(NAME, LAST_NAME, PATRONYMIC, PHONE_NUMBER, MAIL, CONFIRMATION,
 START_ROUTES, CREATION_ACCOUNT, END_CONV, END) = range(10)
name1, last_name1, patronymic1, phone1, mail1 = range(5)

# conn = sqlite3.connect('C:/Users/Redmi/PycharmProjects/pythonTgBot/data/data.db')
# cur = conn.cursor()

bot = Bot(token="7188985096:AAFn7ijrux_O4JAEkJQWeAk3J8V8fg_wJrk")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    # cur.execute("SELECT name FROM users WHERE telegram_id = ?",
    #             (str(chat_id),))
    # row = cur.fetchone()
    # name = row if row else None
    # context.args = ['']
    # context.user_data['command'] = 'info'
    # if name is not None:
    #     await CommandHandler('info', info).callback(update, context.bot)
    # else:
    await update.message.reply_text(
        "Привет, для начала работы давайте создадим вам аккаунт! Вы должны ввести следующие данные (Вводите по "
        "порядку по одному сообщению):\n\n"
        "Фамилия: ❌\n"
        "Имя: ❌\n"
        "Отчество: ❌\n"
        "Телефон: ❌\n"
        "Почта: ❌\n")
    return LAST_NAME

# something
async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "Привет, для начала работы давайте создадим вам аккаунт! Вы должны ввести следующие данные (Вводите по "
        "порядку по одному сообщению):\n\n"
        "Фамилия: ❌\n"
        "Имя: ❌\n"
        "Отчество: ❌\n"
        "Телефон: ❌\n"
        "Почта: ❌\n")

    return LAST_NAME


async def last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_name = update.message.text.capitalize()
    await update.message.reply_text(f"Фамилия: ✅ ({last_name})")
    print(last_name)
    global last_name1
    last_name1 = last_name

    return NAME


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = update.message.text.capitalize()
    await update.message.reply_text(f"Имя: ✅ ({name})")
    global name1
    name1 = name

    return PATRONYMIC


async def patronymic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    patronymic = update.message.text.capitalize()
    await update.message.reply_text(f"Отчество: ✅ ({patronymic})")
    print(patronymic)
    global patronymic1
    patronymic1 = patronymic

    return PHONE_NUMBER


async def phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if (re.match("^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$", phone)) is None:
        await update.message.reply_text("Введите корректный телефон:")
        return PHONE_NUMBER

    await update.message.reply_text(f"Телефон: ✅ ({phone})")
    global phone1
    phone1 = phone

    return CONFIRMATION


async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mail = update.message.text
    if (re.match("^([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)$", mail)) is None:
        await update.message.reply_text("Введите корректный email:")
        return CONFIRMATION

    await update.message.reply_text(f"Почта: ✅ ({mail})")
    global mail1
    mail1 = mail

    keyboard = [[InlineKeyboardButton(text="Подтвердить ✅", callback_data=str(END))],
                [InlineKeyboardButton(text="Изменить ❌\n(Ввести все данные заново)",
                                      callback_data=str(CREATION_ACCOUNT))]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Вы ввели все необходимые данные для регистрации.",
                                    reply_markup=reply_markup)

    return END_CONV


async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = update.effective_chat.id
    await query.answer()

    # cur.execute("INSERT INTO users (last_name, name, patronymic,"
    #             "phone, email, telegram_id) VALUES (?, ?, ?, ?, ?, ?)",
    #             (last_name1, name1, patronymic1, phone1, mail1, chat_id))
    # conn.commit()
    await query.edit_message_text(f"{name1}, спасибо за регистрацию! Нажмите /info")

    return ConversationHandler.END


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="Здесь должна быть информация о боте")


def main() -> None:
    app = ApplicationBuilder().token("7188985096:AAFn7ijrux_O4JAEkJQWeAk3J8V8fg_wJrk").build()

    user_registration = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, name
                )
            ],
            LAST_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, last_name
                )
            ],
            PATRONYMIC: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, patronymic
                )
            ],
            PHONE_NUMBER: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, phone_number
                )
            ],
            CONFIRMATION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, confirmation
                )
            ],
            END_CONV: [
                CallbackQueryHandler(end_conversation, pattern="^" + str(END) + "$")
            ],
        },
        fallbacks=[CallbackQueryHandler(start_over, pattern="^" + str(CREATION_ACCOUNT) + "$")]
    )

    app.add_handler(user_registration)
    app.add_handler(CommandHandler("info", info))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()