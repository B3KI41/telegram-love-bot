import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)

logging.basicConfig(level=logging.INFO)

# Вопросы и ответы
QUESTIONS = [
    {
        "question": "Наша первая встреча?",
        "options": ["Твой подъезд", "Кафе в центре", "Магазин одежды"],
        "correct": "Твой подъезд"
    },
    {
        "question": "Что ты делала, когда впервые пришла ко мне домой?",
        "options": ["Трогала мою голову", "Смотрела телевизор", "Заснула сразу"],
        "correct": "Трогала мою голову"
    },
    {
        "question": "Первое наше совместное мероприятие?",
        "options": ["День Рождение", "Свадьба", "Просто посиделка"],
        "correct": "День Рождение"
    },
    {
        "question": "Первый мой подарок для тебя, который я никому больше не дарил?",
        "options": ["Цветы (51 роза)", "Хромосомы (47)", "Деньги (35 тысяч)"],
        "correct": "Цветы (51 роза)"
    },
    {
        "question": "Мой первый бизнес на Озоне с чем был связан?",
        "options": ["Наборы сладостей", "Игрушки", "Напитки"],
        "correct": "Наборы сладостей"
    },
    {
        "question": "Когда ты была в больнице, за чем любила наблюдать?",
        "options": ["Раствор марганца", "Клизма", "Осмотр горла"],
        "correct": "Раствор марганца"
    }
]

# Загадки
RIDDLES = {
    3: {
        "text": "Загадка про любовь: \n\nЭто чувство между строк,\nЧто растёт с каждым деньком.\nНезаметно, но всерьёз,\nТы и я — и нет угроз 💞",
        "image": "love_photo_1.png"
    },
    6: {
        "text": "Ты всегда можешь положиться на меня. Даже когда всё только начиналось и чувства были ещё не такими сильными, я уже был рядом. И буду всегда. Навсегда.",
        "video": "hospital_circle.mov"
    }
}

STATE = {"index": 0, "history": []}

def get_keyboard(index):
    q = QUESTIONS[index]
    keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in q["options"]]
    if index > 0:
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])
    keyboard.append([InlineKeyboardButton("🔁 Начать заново", callback_data="restart")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    STATE["index"] = 0
    STATE["history"] = []
    await update.message.reply_text("🌸 Привет, любимая! Давай посмотрим, насколько хорошо мы знаем друг друга 😊\n\nГотова?", reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Поехали!", callback_data="start")]]
    ))

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "start":
        STATE["index"] = 0
        STATE["history"] = []
        q = QUESTIONS[STATE["index"]]
        await query.message.reply_text(q["question"], reply_markup=get_keyboard(STATE["index"]))
        return

    if data == "restart":
        STATE["index"] = 0
        STATE["history"] = []
        await query.message.reply_text("🔁 Начинаем сначала!")
        q = QUESTIONS[STATE["index"]]
        await query.message.reply_text(q["question"], reply_markup=get_keyboard(STATE["index"]))
        return

    if data == "back":
        if STATE["index"] > 0:
            STATE["index"] -= 1
            STATE["history"].pop()
        q = QUESTIONS[STATE["index"]]
        await query.message.reply_text(q["question"], reply_markup=get_keyboard(STATE["index"]))
        return

    current_q = QUESTIONS[STATE["index"]]
    STATE["history"].append({"question": current_q["question"], "answer": data})

    if data == current_q["correct"]:
        await query.message.reply_text("✅ Верно!")
    else:
        await query.message.reply_text(f"❌ Неа. Правильный ответ: {current_q['correct']}")

    STATE["index"] += 1

    if STATE["index"] in RIDDLES:
        riddle = RIDDLES[STATE["index"]]
        await query.message.reply_text("🧩 Небольшая загадка!")
        await query.message.reply_text(riddle["text"])
        if "image" in riddle:
            with open(riddle["image"], "rb") as f:
                await query.message.reply_photo(f)
        if "video" in riddle:
            with open(riddle["video"], "rb") as f:
                await query.message.reply_video(f)

    if STATE["index"] < len(QUESTIONS):
        q = QUESTIONS[STATE["index"]]
        await query.message.reply_text(q["question"], reply_markup=get_keyboard(STATE["index"]))
    else:
        await query.message.reply_text("🎉 Это были все вопросы. Спасибо, что прошла этот путь со мной ❤️")

if __name__ == "__main__":
    app = ApplicationBuilder().token("YOUR_TOKEN_HERE").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_answer))
    app.run_polling()
