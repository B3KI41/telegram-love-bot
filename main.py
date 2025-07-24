from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

TOKEN = 'YOUR_BOT_TOKEN'

questions = [
    {
        "question": "Наша первая встреча?",
        "options": ["Твой подъезд", "Дома", "Кафе"],
        "correct": 0
    },
    {
        "question": "Что ты делала, когда пришла впервые ко мне домой?",
        "options": ["Трогала мою голову", "Смотрела телевизор", "Ела пельмени"],
        "correct": 0
    },
    {
        "question": "Первое наше совместное мероприятие?",
        "options": ["День Рождение", "Свадьба", "Просто посиделка"],
        "correct": 0
    },
    {
        "type": "riddle",
        "text": "💌 Маленькая загадка:\n\nО чём-то важном не забудь —\nТвоя поддержка — мой маршрут.\nПлечо моё — не на словах,\nТы можешь положиться, как тогда… ❤️",
        "photo_url": "https://raw.githubusercontent.com/B3KI41/telegram-love-bot/main/love_photo_1.png"
    },
    {
        "question": "Первый мой подарок для тебя, который я никому не дарил ни до, ни после?",
        "options": ["Цветы (51 Роза)", "Хромосомы (47)", "Деньги (35 тысяч)"],
        "correct": 0
    },
    {
        "question": "Мой первый бизнес на Ozon был связан с…?",
        "options": ["Наборы сладостей", "Игрушки", "Напитки"],
        "correct": 0
    },
    {
        "question": "Когда ты попала в больницу, за каким процессом ты любила наблюдать?",
        "options": ["Раствор марганца", "Клизма", "Осмотр горла"],
        "correct": 0
    },
    {
        "type": "riddle",
        "text": "✨ Иногда ты болела, иногда грустила, но ты всегда знала — я рядом. И даже когда было тяжело, я топил за тебя всем сердцем.\n\nТы не одна — никогда. ❤️",
        "video_url": "https://raw.githubusercontent.com/B3KI41/telegram-love-bot/main/hospital_circle.mov"
    }
]

user_states = {}

def get_question_markup(index):
    question = questions[index]
    buttons = [
        [InlineKeyboardButton(text=opt, callback_data=f"answer:{index}:{i}")]
        for i, opt in enumerate(question["options"])
    ]
    if index > 0:
        buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])
    buttons.append([InlineKeyboardButton("🔁 Начать заново", callback_data="restart")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = 0
    await update.message.reply_text(
        "💘 Готова пройти нашу историю заново?\n\nЖми «Поехали»!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Поехали!", callback_data="start")]])
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "start":
        user_states[user_id] = 0
        await send_question(query, user_id)

    elif query.data == "restart":
        user_states[user_id] = 0
        await query.message.reply_text("🔁 Начинаем заново!")
        await send_question(query, user_id)

    elif query.data == "back":
        user_states[user_id] = max(user_states[user_id] - 1, 0)
        await send_question(query, user_id)

    elif query.data.startswith("answer"):
        _, q_index, a_index = query.data.split(":")
        q_index, a_index = int(q_index), int(a_index)
        correct = questions[q_index]["correct"]
        result = "✅ Верно!" if a_index == correct else "❌ Не совсем..."
        await query.message.reply_text(result)

        user_states[user_id] += 1
        await send_question(query, user_id)

async def send_question(query, user_id):
    index = user_states[user_id]
    if index >= len(questions):
        await query.message.reply_text("🏁 Это был конец этой части! Хочешь начать сначала? 🔁", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Начать заново", callback_data="restart")]]))
        return

    q = questions[index]
    if "question" in q:
await query.message.reply_text(q["question"], reply_markup=get_question_markup(index))
    elif q.get("type") == "riddle":
        if "photo_url" in q:
            await query.message.reply_photo(photo=q["photo_url"], caption=q["text"])
        elif "video_url" in q:
            await query.message.reply_video(video=q["video_url"], caption=q["text"])
        user_states[user_id] += 1
        await send_question(query, user_id)

if name == '__main__':
    from telegram.ext import ApplicationBuilder
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()
