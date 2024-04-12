import re
from db import Database
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
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

(NAME, LAST_NAME, PHONE_NUMBER, MAIL, CONFIRMATION,
 START_ROUTES, SHOP, CREATION_ACCOUNT, END_CONV, END,
 ASK_QUESTION, VIEW_QUESTIONS, USER_QUESTION, USER_ANSWER, VIEW_ANSWERS,
 ADD_ANSWER, VIEWING_QUESTION, BUY_ITEM, BACK, ANSWER,
 QUESTION, CHANGING_ANSWER, CHANGING_QUESTION, TAGS, SEARCH,
 UPDATE_RATING, BAD_QUESTION, GOOD_QUESTION, LOGIN, PASSWORD,
 ADMIN, REQUEST, DECISION_ANSWER, DECISION_QUESTION, CONTINUE_REVIEW,
 ACCESS) = map(chr, range(36))

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
        [InlineKeyboardButton("Просмотреть все вопросы", callback_data=str(VIEW_QUESTIONS))],
        [InlineKeyboardButton("Поиск вопроса по тегу", callback_data=str(SEARCH))]
    ]
    welcome_message = (f"Привет, {update.effective_user.first_name}!"
                       f" Добро пожаловать в нашего телеграм бота. Я готов помочь тебе с любыми вопросами.")

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

    return START_ROUTES


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await bot.send_message(chat_id=query.from_user.id, text="Введите 🏷 #тег")
    return TAGS


async def tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tag = update.message.text
    rows = db.search_by_tag(tag)
    if len(rows) == 0:
        await bot.send_message(update.message.chat_id, text=f"Тег 🏷 {tag} не найден")
        return TAGS
    else:
        for row in rows:
            question_id, text, date, user_id = row
            keyboard = [
                [InlineKeyboardButton(f"Открыть", callback_data=question_id)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await bot.send_message(chat_id=update.message.chat_id,
                                   text=f"❔ Вопрос: {text}\n"
                                        f"🏷 #тег: {tag}",
                                   reply_markup=reply_markup)

    return START_ROUTES


async def ask_question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await bot.send_message(update.effective_user.id,
                           text="Напишите ваш запрос на знание! После вопроса, через '-' укажите #тег")

    return USER_QUESTION


async def user_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text.split("-")
    text = question[0].strip()
    tag = question[1].strip()
    chat_id = update.effective_chat.id
    db.add_question(chat_id, text, tag)
    await update.message.reply_text(text=f"Спасибо за ваш вопрос! Вам начислено: 1 💎 gems!")
    db.insert_gems(chat_id, 1)
    return ConversationHandler.END


async def all_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    rows = db.all_questions()
    await bot.send_message(chat_id=chat_id, text=f"Вот все запросы на знание:")
    for row in rows:
        tag, question_id, question_text, rating = row
        keyboard = [
            [InlineKeyboardButton(f"Открыть", callback_data=question_id)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(chat_id=chat_id,
                               text=f"❔ Вопрос: {question_text}\n"
                                    f"🏷 #тег: {tag}\n"
                                    f"📈 Рейтинг: {rating}",
                               reply_markup=reply_markup)

    return START_ROUTES


async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question"] = int(update.callback_query.data)
    await update.callback_query.answer()
    row = db.get_question(context.user_data["question"])
    tag, question_text, date, user_id, rating = row
    user_lastname, username = db.get_user(user_id)
    keyboard = [
        [InlineKeyboardButton("Ответить на запрос", callback_data=str(ADD_ANSWER))],
        [InlineKeyboardButton("Просмотреть все ответы", callback_data=str(VIEW_ANSWERS))],
        [InlineKeyboardButton("Плохой вопрос 🔻", callback_data=str(BAD_QUESTION)),
         InlineKeyboardButton("Хороший вопрос ✅", callback_data=str(GOOD_QUESTION))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=update.effective_user.id,
                           text=f"❔ Вопрос: {question_text}\n\n"
                                f"🏷 #тег: {tag}\n"
                                f"📈 Рейтинг: {rating}\n"
                                f"⏰ Время: {date}\n"
                                f"👤 Пользователь: {user_lastname} {username}",
                           reply_markup=reply_markup)
    return START_ROUTES


async def set_question_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    vote = 0
    if query.data == str(BAD_QUESTION):
        vote = -2
    keyboard = [[InlineKeyboardButton(text="↩", callback_data=context.user_data["question"])]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    db.set_question_rating(context.user_data["question"], vote)
    await bot.send_message(chat_id=update.effective_user.id, text="Ваш голос учтен!", reply_markup=reply_markup)
    return START_ROUTES


async def user_answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await bot.send_message(chat_id=update.effective_user.id, text="Напишите ваш ответ:")

    return USER_ANSWER


async def user_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_user.id
    question_id = context.user_data["question"]
    db.add_answer(chat_id, text, question_id)
    row = db.check_strike(chat_id)
    today_answers = row[0]
    if today_answers in [3, 4, 5]:
        await update.message.reply_text(text=f"Вау! Ты много знаешь! За сегодня ты ответил на {today_answers} "
                                             f"запроса на знание! Держи 💎 {today_answers + 2} gems!"
                                             f"\n\nДля возврата в меню, нажмите /info")
        db.insert_gems(chat_id, today_answers + 2)
    elif today_answers in [6, 7, 8, 9]:
        await update.message.reply_text(text=f"Да ты знаток производства! Молодец! За сегодня ты ответил на "
                                             f"{today_answers} "
                                             f"запроса на знание! Держи 💎 {today_answers + 3} gems!"
                                             f"\n\nДля возврата в меню, нажмите /info")
        db.insert_gems(chat_id, today_answers + 3)
    elif today_answers >= 10:
        await update.message.reply_text(text=f"Магистр знаний!!! К вам всегда можно обратиться с вопросом! "
                                             f"За сегодня ты ответил на {today_answers} "
                                             f"запросов на знание! Держи 💎 {today_answers + 5} gems!"
                                             f"\n\nДля возврата в меню, нажмите /info")
        db.insert_gems(chat_id, today_answers + 5)
    else:
        await update.message.reply_text(text="Спасибо за ваш ответ! Вам начислено: 💎 1 gem!"
                                             "\n\nДля возврата в меню, нажмите /info")
        db.insert_gems(chat_id, 1)
    context.user_data.clear()

    return ConversationHandler.END


async def view_answers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    question_id = context.user_data["question"]
    rows = db.all_answers(question_id)
    if len(rows) == 0:
        await bot.send_message(chat_id=update.effective_user.id, text='На этот вопрос пока нет ответов')
    for row in rows:
        answer_id, text, date, user_id = row
        user_lastname, username = db.get_user(user_id)
        await bot.send_message(chat_id=update.effective_user.id,
                               text=f"Ответ от: {user_lastname} {username}\n\n"
                                    f"{text}\n\n"
                                    f"⏰ Время: {date}\n")
    keyboard = [[InlineKeyboardButton(text="↩", callback_data=question_id)]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=update.effective_user.id, text='Вы можете вернуться назад',
                           reply_markup=reply_markup)
    context.user_data.clear()
    return START_ROUTES


async def get_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    rows = db.all_users()
    for row in rows:
        last_name, name, phone_number, email, count_answers, count_questions = row
        await bot.send_message(chat_id=update.effective_user.id, text=f"Пользователь:{last_name} {name}\n\n"
                                                                      f"Количество ответов: {count_answers}\n"
                                                                      f"Количество запросов на знания: {count_questions}\n\n"
                                                                      f"Телефон: {phone_number}\n"
                                                                      f"Почта: {email}")


async def account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    last_name, name, phone_number, email, gems = db.account(chat_id)
    await update.message.reply_text(text=f"Ваш аккаунт:\n\n"
                                         f"Фамилия: {last_name}\n"
                                         f"Имя: {name}\n"
                                         f"Телефон: {phone_number}\n"
                                         f"Почта: {email}\n"
                                         f"Баланс: 💎 {gems} gems")


async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    keyboard = [[InlineKeyboardButton(text="1️⃣", callback_data=10),
                 InlineKeyboardButton(text="2️⃣", callback_data=25),
                 InlineKeyboardButton(text="3️⃣", callback_data=50),
                 InlineKeyboardButton(text="4️⃣", callback_data=100)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=f"Добро пожаловать в магазин! Здесь вы можете приобрести товары, услуги и тд."
                                         f"за 💎 gems, достаточно нажать на кнопку, и товар ваш!\n\n"
                                         f"Ваш баланс: 💎 {db.get_gems(chat_id)[0]} gems\n\n"
                                         f"Товары:\n\n"
                                         f"1️⃣ Item1 - 10 💎 gems\nDescription1\n\n"
                                         f"2️⃣ Item2 - 25 💎 gems\nDescription2\n\n"
                                         f"3️⃣ Item3 - 50 💎 gems\nDescription3\n\n"
                                         f"4️⃣ Item4 - 100 💎 gems\nDescription2",
                                    reply_markup=reply_markup)

    return BUY_ITEM


async def shop_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    keyboard = [[InlineKeyboardButton(text="1️⃣", callback_data=10),
                 InlineKeyboardButton(text="2️⃣", callback_data=25),
                 InlineKeyboardButton(text="3️⃣", callback_data=50),
                 InlineKeyboardButton(text="4️⃣", callback_data=100)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"Добро пожаловать в магазин! Здесь вы можете приобрести товары, услуги и тд."
                                       f"за 💎 gems, достаточно нажать на кнопку, и товар ваш!\n\n"
                                       f"Ваш баланс: 💎 {db.get_gems(chat_id)[0]} gems\n\n"
                                       f"Товары:\n\n"
                                       f"1️⃣ Item1 - 10 💎 gems\nDescription1\n\n"
                                       f"2️⃣ Item2 - 25 💎 gems\nDescription2\n\n"
                                       f"3️⃣ Item3 - 50 💎 gems\nDescription3\n\n"
                                       f"4️⃣ Item4 - 100 💎 gems\nDescription2",
                                  reply_markup=reply_markup)

    return BUY_ITEM


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # await query.answer()
    chat_id = update.effective_chat.id
    gems = db.get_gems(chat_id)[0]
    keyboard = [[InlineKeyboardButton(text="↩", callback_data=str(SHOP))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if gems <= int(query.data):
        await query.edit_message_text(
            text="❌ Недостаточно средств",
            reply_markup=reply_markup)
        return BACK
    else:
        db.insert_gems(chat_id, -int(query.data))
        await bot.send_message(chat_id=update.effective_user.id, text=f"✅ Товар успешно куплен!\n"
                                                                      f"Ваш баланс: {db.get_gems(chat_id)[0]} 💎 gems")

    return ConversationHandler.END


async def get_my_answers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    rows = db.my_answers(chat_id)
    for row in rows:
        answer_id, text_answer, answer_date, question_id = row
        tag, text_question, question_date, asker_id, rating = db.get_question(question_id)
        asker_last_name, asker_name = db.get_user(asker_id)
        keyboard = [[InlineKeyboardButton(text="✏ Изменить", callback_data=answer_id)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(chat_id=chat_id, text=f"Вопрос:\n{text_question}\nОт: {asker_last_name} {asker_name}\n"
                                                     f"Дата: {question_date}\n\nВаш ответ: {text_answer}\n"
                                                     f"Дата: {answer_date}", reply_markup=reply_markup)

    return CHANGING_ANSWER


async def change_my_answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["answer_id"] = int(update.callback_query.data)
    chat_id = update.effective_chat.id
    await bot.send_message(chat_id=chat_id, text="Напишите ваш ответ")
    return ANSWER


async def change_my_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer_id = context.user_data["answer_id"]
    db.update_answer(text, answer_id)
    await update.message.reply_text(text="Изменения сохранены")
    context.user_data.clear()
    return CHANGING_ANSWER


async def get_my_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    rows = db.my_questions(chat_id)
    for row in rows:
        question_id, text, date = row
        keyboard = [[InlineKeyboardButton(text="✏ Изменить", callback_data=question_id)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(chat_id=chat_id, text=f"Вопрос:\n{text}\n"
                                                     f"Дата: {date}\n",
                               reply_markup=reply_markup)

    return CHANGING_QUESTION


async def change_my_question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question_id"] = int(update.callback_query.data)
    chat_id = update.effective_chat.id
    await bot.send_message(chat_id=chat_id, text="Напишите ваш вопрос")
    return QUESTION


async def change_my_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    question_id = context.user_data["question_id"]
    db.update_question(text, question_id)
    await update.message.reply_text(text="Изменения сохранены")
    context.user_data.clear()
    return ConversationHandler.END


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    keyboard = [[InlineKeyboardButton("Войти", callback_data=str(ADMIN))]]
    await bot.send_message(chat_id, text="Раздел администратора", reply_markup=InlineKeyboardMarkup(keyboard))
    return LOGIN


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = update.effective_chat.id
    if db.check_admin(chat_id) is False:
        await bot.send_message(chat_id, "Вы не admin")
        return ConversationHandler.END
    await bot.send_message(chat_id, "Введите логин")
    return PASSWORD


async def password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    await update.message.reply_text("Введите пароль")
    return ACCESS


async def access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    admin = True
    chat_id = update.effective_user.id
    if update.message is not None:
        password = update.message.text
        username = context.user_data.get('username')
        admin = db.check_entry_admin(chat_id, username, password)
    keyboard = [[InlineKeyboardButton("Просмотреть все вопросы", callback_data=str(VIEW_QUESTIONS)),
                 InlineKeyboardButton("Просмотреть все ответы", callback_data=str(VIEW_ANSWERS))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if not admin:
        await update.message.reply_text("Неверный логин или пароль. Попробуйте снова: /admin")
        return ADMIN
    await bot.send_message(chat_id, "Добро пожаловать в раздел администратора! "
                                    "Здесь вы можете просмотреть все запросы на знания", reply_markup=reply_markup)
    return REQUEST


async def review_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    if query.data == str(VIEW_QUESTIONS):
        rows = db.all_questions(state=False, decline=True)
        if len(rows) == 0:
            keyboard = [
                [InlineKeyboardButton("Вернуться назад", callback_data='Вернуться назад')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="Новых запросов на знание пока нет.", reply_markup=reply_markup)
            return ACCESS
        for row in rows:
            tag, question_id, question_text, rating = row
            db.set_true_question(question_id, True)
            await bot.send_message(chat_id=chat_id,
                                   text=f"❔ Вопрос: {question_text}\n"
                                        f"🏷 #тег: {tag}\n"
                                        f"📈 Рейтинг: {rating}\n"
                                        f"QUESTION_ID: {question_id}")

        await bot.send_message(chat_id=chat_id, text="Напишите через запятую id вопросов, которые следует принять, "
                                                     "остальные будут отклонены. Если все следует отклонить, напишите 0")
        return DECISION_QUESTION
    else:
        rows = db.all_questions(state=True, decline=False)
        count_ans = False
        for row in rows:
            tag, question_id, question_text, rating = row
            answers = db.all_answers(question_id=question_id, state=False, decline=True)
            if len(answers) == 0:
                continue
            count_ans = True
            await bot.send_message(chat_id=chat_id,
                                   text=f"➖➖➖➖➖➖➖➖➖➖➖")
            await bot.send_message(chat_id=chat_id,
                                   text=f"❔ Вопрос: {question_text}\n\nОтветы:")
            for answer in answers:
                answer_id, text, date, user_id = answer
                db.set_true_answer(answer_id, True)
                await bot.send_message(chat_id=chat_id, text=f"{text}\nANSWER_ID: {answer_id}")
        if count_ans:
            await bot.send_message(chat_id=chat_id, text="Напишите через запятую id ответов, которые следует принять, "
                                                         "остальные будут отклонены. Если все следует отклонить, "
                                                         "напишите 0")
            return DECISION_ANSWER
        else:
            keyboard = [
                [InlineKeyboardButton("Вернуться назад", callback_data='Вернуться назад')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="Новых ответов пока нет.", reply_markup=reply_markup)
            return ACCESS


async def decision_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accepted_questions = update.message.text.split(',')
    chat_id = update.effective_chat.id
    for accepted_question in accepted_questions:
        db.set_true_question(int(accepted_question))

    keyboard = [
        [InlineKeyboardButton("Вернуться назад", callback_data='Вернуться назад')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=chat_id, text="Решение принято.", reply_markup=reply_markup)

    return CONTINUE_REVIEW


async def decision_answers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accepted_answers = update.message.text.split(',')
    chat_id = update.effective_chat.id
    for accepted_answer in accepted_answers:
        print(accepted_answer)
        db.set_true_answer(int(accepted_answer))

    keyboard = [
        [InlineKeyboardButton("Вернуться назад", callback_data='Вернуться назад')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=chat_id, text="Решение принято.", reply_markup=reply_markup)

    return CONTINUE_REVIEW

async def handle_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    decision = update.callback_query.data
    if decision == 'accept':
        await update.callback_query.message.reply_text("new idea has been sent to all users.")
    elif decision == 'decline':
        user_id = update.callback_query.message.chat_id
        await context.bot.send_message(chat_id=user_id, text="your idea request has been declined.")

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
                CallbackQueryHandler(ask_question_handler, pattern="^" + str(ASK_QUESTION) + "$"),
                CallbackQueryHandler(all_questions, pattern="^" + str(VIEW_QUESTIONS) + "$"),
                CallbackQueryHandler(question, pattern="^-?\d+(\.\d+)?$"),
                CallbackQueryHandler(view_answers, pattern="^" + str(VIEW_ANSWERS) + "$"),
                CallbackQueryHandler(user_answer_handler, pattern="^" + str(ADD_ANSWER) + "$"),
                CallbackQueryHandler(search, pattern="^" + str(SEARCH) + "$"),
                CallbackQueryHandler(set_question_rating, pattern="^" + str(BAD_QUESTION) + "$"),
                CallbackQueryHandler(set_question_rating, pattern="^" + str(GOOD_QUESTION) + "$")
            ],
            USER_QUESTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, user_question
                )
            ],
            USER_ANSWER: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, user_answer
                )
            ],
            TAGS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, tags
                )
            ],
            UPDATE_RATING: [
                CallbackQueryHandler(question, pattern="^-?\d+(\.\d+)?$")
            ]
        },
        fallbacks=[CallbackQueryHandler(question, pattern="^-?\d+(\.\d+)?$")]
    )

    buy_item = ConversationHandler(
        entry_points=[CommandHandler("shop", shop)],
        states={
            BUY_ITEM: [
                CallbackQueryHandler(buy, pattern="^-?\d+(\.\d+)?$")
            ],
            BACK: [
                CallbackQueryHandler(shop_over, pattern="^" + str(SHOP) + "$")
            ],
        },
        fallbacks=[]
    )

    changing_answer = ConversationHandler(
        entry_points=[CommandHandler("myanswers", get_my_answers),
                      CommandHandler("myquestions", get_my_questions)],
        states={
            CHANGING_ANSWER: [
                CallbackQueryHandler(change_my_answer_handler, pattern="^-?\d+(\.\d+)?$")
            ],
            CHANGING_QUESTION: [
                CallbackQueryHandler(change_my_question_handler, pattern="^-?\d+(\.\d+)?$")
            ],
            ANSWER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_my_answer)
            ],
            QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, change_my_question)
            ]
        },
        fallbacks=[]
    )

    admin_panel = ConversationHandler(
        entry_points=[CommandHandler("admin", admin)],
        states={
            LOGIN: [CallbackQueryHandler(login, pattern="^" + str(ADMIN) + "$")],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password)],
            ACCESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, access),
                     CallbackQueryHandler(access, pattern="^" + "Вернуться назад" + "$")],
            REQUEST: [CallbackQueryHandler(review_request, pattern="^" + str(VIEW_QUESTIONS) + "$"),
                      CallbackQueryHandler(review_request, pattern="^" + str(VIEW_ANSWERS) + "$")],
            DECISION_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, decision_answers)],
            DECISION_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, decision_questions)],
            CONTINUE_REVIEW: [CallbackQueryHandler(access, pattern="^" + "Вернуться назад" + "$")]
        },
        fallbacks=[CommandHandler("admin", admin)]
    )

    app.add_handler(admin_panel)
    app.add_handler(user_registration)
    app.add_handler(welcome_message)
    app.add_handler(buy_item)
    app.add_handler(changing_answer)
    app.add_handler(CommandHandler("account", account))
    app.add_handler(CommandHandler("users", get_all_users))
    app.add_handler(CommandHandler("info", info))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
