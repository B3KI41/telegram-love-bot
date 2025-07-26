import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

TOKEN = "8222070472:AAHHZEU9SJISEMmmXvvCMHeUSPXcZy_JhO0"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Вопросы, варианты, правильные ответы, вставки и медиа
QUESTIONS = [
    {
        "text": "1️⃣ Наша первая встреча 🌆",
        "options": ["Универ", "Твой подъезд", "Кинотеатр", "Магазин у дома"],
        "correct": "Твой подъезд",
    },
    {
        "text": "2️⃣ Что ты сказала после нашей первой прогулки? 💬",
        "options": ["Ну… нормально", "Ты милый", "Я устала", "Было здорово"],
        "correct": "Было здорово",
    },
    {
        "text": "3️⃣ Какая песня стала «нашей» первой? 🎶",
        "options": ["Артем Качер – Девочка", "Jony – Комета", "Miyagi – Minor", "Макс Корж – Малый повзрослел"],
        "correct": "Jony – Комета",
    },
    {
        "insert": {
            "type": "puzzle",
            "question": "❤️ Загадка: Что всегда рядом, даже в молчании? Что греет душу, даже когда холодно? Что ты всегда можешь почувствовать, даже не видя?..",
            "options": ["Любовь", "Понимание", "Слова", "Тишина"],
            "correct": "Любовь",
            "after_text": "Это была наша первая настоящая любовь… Чистая, искренняя, как тот вечер, когда мы просто сидели рядом — и больше ничего не было нужно.",
            "media": {
                "type": "photo",
                "path": "media/love_photo.jpg"  # Путь к вашей общей фотографии
            }
        }
    },
    {
        "text": "4️⃣ Что ты больше всего ценишь в отношениях? 💞",
        "options": ["Честность", "Забота", "Подарки", "Внимание"],
        "correct": "Забота",
    },
    {
        "text": "5️⃣ Когда я впервые тебе сказал, что люблю? 💌",
        "options": ["Вечером в машине", "По телефону", "На прогулке", "В переписке"],
        "correct": "Вечером в машине",
    },
    {
        "text": "6️⃣ Что тебе особенно запомнилось в больнице? 🏥",
        "options": ["Моя поддержка", "Врачи", "Скука", "Боль"],
        "correct": "Моя поддержка",
    },
    {
        "insert": {
            "type": "puzzle",
            "question": "🤍 Загадка: Что остаётся, когда всё рушится? Что можно услышать в голосе без слов? Что не уходит, даже если больно?",
            "options": ["Поддержка", "Смех", "Надежда", "Сон"],
            "correct": "Поддержка",
            "after_text": "И даже тогда, когда мы были чуть знакомы, ты могла положиться на меня. Я рядом. Всегда.",
            "media": {
                "type": "video",
                "path": "media/hospital_circle.mov"  # Путь к кружку из больницы
            }
        }
    },
]

current_question = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Поехали! 🚀", callback_data="start_quiz")]]
    await update.message.reply_text("Привет, любимая! 💌 Готова пройти наше путешествие по воспоминаниям?", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "start_quiz":
        current_question[user_id] = 0
        await send_question(update, context, user_id)
    elif query.data.startswith("answer:"):
        _, chosen = query.data.split(":", 1)
        index = current_question.get(user_id, 0)
        q = QUESTIONS[index]

        if "text" in q:  # обычный вопрос
            if chosen == q["correct"]:
                reply = "✅ Верно!"
            else:
                reply = f"❌ Не совсем… Правильный ответ: {q['correct']}"
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(reply)
        elif "insert" in q:  # загадка
            correct = q["insert"]["correct"]
            if chosen == correct:
                reply = "🌟 Угадала!"
            else:
                reply = f"😔 Почти… Это была: {correct}"
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(reply)

            # отправка текста и медиа
            if q["insert"].get("after_text"):
                await query.message.reply_text(q["insert"]["after_text"])
            if q["insert"]["media"]["type"] == "photo":
                await query.message.reply_photo(open(q["insert"]["media"]["path"], "rb"))
            elif q["insert"]["media"]["type"] == "video":
                await query.message.reply_video(open(q["insert"]["media"]["path"], "rb"))

        current_question[user_id] += 1
        await send_question(update, context, user_id)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    index = current_question.get(user_id, 0)
    if index >= len(QUESTIONS):
        await context.bot.send_message(chat_id=user_id, text="🎉 Это был лишь кусочек нашей истории. Спасибо, что ты есть 💕")
        return

    q = QUESTIONS[index]

    if "text" in q:  # обычный вопрос
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"answer:{opt}")] for opt in q["options"]]
        await context.bot.send_message(chat_id=user_id, text=q["text"], reply_markup=InlineKeyboardMarkup(keyboard))
    elif "insert" in q:
        puzzle = q["insert"]
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"answer:{opt}")] for opt in puzzle["options"]]
        await context.bot.send_message(chat_id=user_id, text=f"🧩 {puzzle['question']}", reply_markup=InlineKeyboardMarkup(keyboard))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_query))
    app.run_polling()
