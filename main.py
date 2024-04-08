import re
import psycopg2
import requests
import telegram
from db import Database
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
 START_ROUTES, CREATION_ACCOUNT, END_CONV, END, ASK_QUESTION, VIEW_QUESTIONS, USER_QUESTION) = range(13)


db = Database("project", "bot", "bot123", "194.87.239.80", "5432")


bot = Bot(token="7188985096:AAFn7ijrux_O4JAEkJQWeAk3J8V8fg_wJrk")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if db.user_exists(chat_id) is not False:
        await update.message.reply_text(text="Привет! Нажми /info.")
        return ConversationHandler.END
    else:
        chat_id = update.effective_chat.id
        db.add_user(chat_id)
        await update.message.reply_text(
            "Привет, для начала работы давайте создадим вам аккаунт! Вы должны ввести следующие данные (Вводите по "
            "порядку по одному сообщению):\n\n"
            "Фамилия: ❌\n"
            "Имя: ❌\n"
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
        "Телефон: ❌\n"
        "Почта: ❌\n")

    return LAST_NAME


async def last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_name = update.message.text.capitalize()
    await update.message.reply_text(f"Фамилия: ✅ ({last_name})")
    chat_id = update.effective_chat.id
    db.set_last_name(chat_id, last_name)

    return NAME


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = update.message.text.capitalize()
    await update.message.reply_text(f"Имя: ✅ ({name})")
    chat_id = update.effective_chat.id
    db.set_name(chat_id, name)
    return PHONE_NUMBER


async def phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if (re.match("^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$", phone)) is None:
        await update.message.reply_text("Введите корректный телефон:")
        return PHONE_NUMBER

    await update.message.reply_text(f"Телефон: ✅ ({phone})")
    chat_id = update.effective_chat.id
    db.set_phone(chat_id, phone)

    return CONFIRMATION


async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mail = update.message.text
    if (re.match("^([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)$", mail)) is None:
        await update.message.reply_text("Введите корректный email:")
        return CONFIRMATION

    await update.message.reply_text(f"Почта: ✅ ({mail})")
    chat_id = update.effective_chat.id
    db.set_email(chat_id, mail)

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

    await query.edit_message_text("Cпасибо за регистрацию!\nНажмите /info")

    return ConversationHandler.END

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    keyboard = [
        [InlineKeyboardButton("Задать вопрос", callback_data=str(ASK_QUESTION))],
        [InlineKeyboardButton("Просмотреть все вопросы", callback_data=str(VIEW_QUESTIONS))]
    ]
    welcome_message = (f"Привет, {update.effective_user.first_name}!"
                       f" Добро пожаловать в нашего телеграм бота. Я готов помочь тебе с любыми вопросами.")

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    return START_ROUTES


async def ask_question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Напишите ваш запрос на знание.")

    return USER_QUESTION

async def user_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(text=f"Вы написали: {text}.")

    return ConversationHandler.END

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

    welcome_message = ConversationHandler(
        entry_points=[CommandHandler("info", info)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(ask_question_handler, pattern="^" + str(ASK_QUESTION) + "$")
            ],
            USER_QUESTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, user_question
                )
            ],
        },
        fallbacks=[]
    )

    app.add_handler(user_registration)
    app.add_handler(welcome_message)
    app.add_handler(CommandHandler("info", info))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()