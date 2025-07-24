import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import (
    ApplicationBuilder, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters
)

# Вопросы и ответы
QUESTIONS = [
    {
        "question": "Наша первая встреча?",
        "options": ["Твой подъезд", "Парк", "Универ"],
        "answer": "Твой подъезд"
    },
    {
        "question": "Что ты делала, когда впервые пришла ко мне домой?",
        "options": ["Трогала мою голову", "Смотрела телек", "Ругалась"],
        "answer": "Трогала мою голову"
    },
    {
        "question": "Первое наше совместное мероприятие?",
        "options": ["День Рождения", "Свадьба", "Посиделка"],
        "answer": "День Рождения"
    },
    {
        "question": "Первый мой подарок для тебя, который я никому больше не дарил?",
        "options": ["Цветы (51 роза)", "Хромосомы (47)", "Деньги (35 тыс)"],
        "answer": "Цветы (51 роза)"
    },
    {
        "question": "Мой первый бизнес на Озоне был связан с...",
        "options": ["Наборы сладостей", "Игрушки", "Напитки"],
        "answer": "Наборы сладостей"
    },
    {
        "question": "Когда ты попала в больницу, тебе нравилось наблюдать за...",
        "options": ["Раствором марганца", "Клизмой", "Осмотром горла"],
        "answer": "Раствором марганца"
    },
]

PHOTO_URL = "https://raw.githubusercontent.com/B3KI41/telegram-love-bot/main/love_photo_1.png"
VIDEO_URL = "https://raw.githubusercontent.com/B3KI41/telegram-love-bot/main/hospital_circle.mov"

user_state = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_keyboard(options):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=opt, callback_data=opt)] for opt in options
    ] + [
        [InlineKeyboardButton("⬅️ Назад", callback_data="back")],
        [InlineKeyboardButton("🔁 Начать заново", callback_data="restart")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_state[user_id] = {"index": 0, "answers": []}
    await update.message.reply_text("❤️ Привет! Давай проверим, насколько хорошо мы знаем друг друга!\n\nЖми «Поехали»!", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Поехали", callback_data="start_quiz")]
    ]))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "restart":
        user_state[user_id] = {"index": 0, "answers": []}
        await query.message.reply_text("🔁 Всё по новой! Жми «Поехали»", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Поехали", callback_data="start_quiz")]
        ]))
        return

    if data == "start_quiz":
        await send_question(query, context, user_id)
        return

    if data == "back":
        if user_state[user_id]["index"] > 0:
            user_state[user_id]["index"] -= 1
        await send_question(query, context, user_id)
        return

    # Сохранение ответа
    index = user_state[user_id]["index"]
    user_state[user_id]["answers"].append(data)
    user_state[user_id]["index"] += 1

    if user_state[user_id]["index"] == 3:
        await query.message.reply_photo(PHOTO_URL, caption="🪄 Загадка:\nЧто бы ни случилось, знай — моё плечо всегда рядом, даже если нам сложно. Ты можешь положиться на меня всегда.")
        await send_question(query, context, user_id)
    elif user_state[user_id]["index"] == 6:
        await query.message.reply_video(VIDEO_URL, caption="🌀 Помнишь это видео?.. Это навсегда осталось в моём сердце.\nЗагадка: За что бы ты меня ни винила, я всё равно всегда буду рядом.")
        await send_question(query, context, user_id)
    elif user_state[user_id]["index"] < len(QUESTIONS):
        await send_question(query, context, user_id)
    else:
        await query.message.reply_text("💖 Это было потрясающе! Ты прошла все вопросы. Дальше будет ещё интереснее!")

async def send_question(query, context, user_id):
    index = user_state[user_id]["index"]
    q = QUESTIONS[index]
    text = f"{index+1}. {q['question']}"
    await query.message.reply_text(text, reply_markup=get_keyboard(q["options"]))

def main():
    from os import getenv
    TOKEN = getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))

    app.run_polling()

if __name__ == "__main__":
    main()
