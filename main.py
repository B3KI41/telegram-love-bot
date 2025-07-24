import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackContext, CallbackQueryHandler, CommandHandler, ContextTypes

TOKEN = "8222070472:AAHHZEU9SJISEMmmXvvCMHeUSPXcZy_JhO0"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

questions = [
    {
        "text": "Наша первая встреча?",
        "options": ["Твой подъезд", "Универмаг", "Клуб"],
        "answer": "Твой подъезд"
    },
    {
        "text": "Что ты делала, когда впервые пришла ко мне домой?",
        "options": ["Трогала мою голову", "Клеила обои", "Смотрела в зеркало"],
        "answer": "Трогала мою голову"
    },
    {
        "text": "Первое наше совместное мероприятие?",
        "options": ["День Рождение", "Свадьба", "Просто посиделка"],
        "answer": "День Рождение"
    },
    {
        "type": "puzzle",
        "text": "Загадка: Нас мало связывало в самом начале. Но ты знала: я рядом, даже если молчу. Даже если ты в больнице, в слезах, в одиночестве — всегда есть одно место, где тебе спокойно.\n\nЧто это?",
        "options": ["Твоё плечо", "Плед", "Телефон"],
        "answer": "Твоё плечо",
        "media": "https://raw.githubusercontent.com/B3KI41/telegram-love-bot/main/love_photo_1.png"
    },
    {
        "text": "Первый мой подарок для тебя, который я никому больше не дарил?",
        "options": ["Цветы (51 роза)", "Хромосомы (47)", "Деньги (35 тысяч)"],
        "answer": "Цветы (51 роза)"
    },
    {
        "text": "Мой первый бизнес на Ozon с чем был связан?",
        "options": ["Наборы сладостей", "Игрушки", "Напитки"],
        "answer": "Наборы сладостей"
    },
    {
        "text": "Когда ты попала в больницу, ты любила наблюдать за одним процессом. Каким?",
        "options": ["Раствор марганца", "Клизма", "Осмотр горла"],
        "answer": "Раствор марганца"
    },
    {
        "type": "puzzle",
        "text": "Загадка: Что бы ни происходило — ты всегда можешь опереться на меня. Не важно, как далеко, не важно, что между нами. Я рядом. Всегда.\n\nЧто это?",
        "options": ["Моя поддержка", "Прошлое", "Плед"],
        "answer": "Моя поддержка",
        "media": "https://raw.githubusercontent.com/B3KI41/telegram-love-bot/main/hospital_circle.mov"
    }
]

user_data = {}

def get_question_keyboard(index):
    q = questions[index]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(opt, callback_data=opt)] for opt in q["options"]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = 0
    await update.message.reply_text(
        "❤️ Привет! Это наш маленький тест о нашей истории. Давай проверим, как хорошо ты всё помнишь 🥹\n\nНажми на кнопку ниже, чтобы начать 👇",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Поехали!", callback_data="start")]])
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "start":
        user_data[user_id] = 0
    elif query.data == "restart":
        user_data[user_id] = 0
        await query.message.reply_text("🔁 Начинаем сначала!")
    
    index = user_data.get(user_id, 0)
    if index >= len(questions):
        await query.message.reply_text("🎉 Тест завершён! Спасибо за воспоминания 💖")
        return

    q = questions[index]

    if q.get("type") == "puzzle":
        if "media" in q:
            if q["media"].endswith((".jpg", ".png", ".jpeg")):
                await query.message.reply_photo(photo=q["media"], caption=q["text"], reply_markup=get_question_keyboard(index))
            elif q["media"].endswith((".mp4", ".mov")):
                await query.message.reply_video(video=q["media"], caption=q["text"], reply_markup=get_question_keyboard(index))
        else:
            await query.message.reply_text(q["text"], reply_markup=get_question_keyboard(index))
        return

    await query.message.reply_text(q["text"], reply_markup=get_question_keyboard(index))
async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    index = user_data.get(user_id, 0)
    question = questions[index]
    correct = question["answer"]

    if query.data == correct:
        await query.message.reply_text("✅ Верно!")
        user_data[user_id] += 1
        await button_handler(update, context)
    else:
        await query.message.reply_text("❌ Неправильно. Попробуй снова!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(start|restart)$"))
    app.add_handler(CallbackQueryHandler(answer_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
