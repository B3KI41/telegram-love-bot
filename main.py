import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackContext, CallbackQueryHandler, CommandHandler, ContextTypes

TOKEN = "8222070472:AAHHZEU9SJISEMmmXvvCMHeUSPXcZy_JhO0"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

questions = [
    {
        "question": "✨ *Наша первая встреча...*\nПомнишь, где это было?\nГде мы впервые увиделись?",
        "options": ["Твой подъезд", "Мой институт", "Магазин у дома"],
        "correct_option": 0
    },
    {
        "question": "😌 *Когда ты впервые пришла ко мне домой…*\nЯ немного нервничал, если честно.\nЧто ты сделала первым делом? 🙈",
        "options": ["Трогала мою голову", "Пересмотрела мою еду в холодильнике", "Спала на диване"],
        "correct_option": 0
    },
    {
        "question": "🎈 *Наше первое совместное событие…*\nЯ так старался сделать этот день особенным.\nЧто это было?",
        "options": ["День Рождения", "Свадьба", "Посиделка с друзьями"],
        "correct_option": 0
    },
    {
        "is_riddle": True,
        "riddle_type": "love",
        "riddle_text": "Она тихо приходит, не кричит и не требует.\nОна в мелочах и взглядах, в тишине и в объятиях.\nЧто это?",
        "riddle_answer": "Настоящая любовь ❤️",
        "image_url": "https://raw.githubusercontent.com/B3KI41/telegram-love-bot/main/love_photo_1.png",
        "riddle_response": "Знаешь, я часто думал о том, как всё началось.\nТы — моя первая настоящая любовь.\nИ я всегда это буду помнить."
    },
    {
        "question": "🥀 *Помнишь мой первый подарок, который был только для тебя?*\nЯ никогда никому не дарил такое до тебя.\nЧто это было?",
        "options": ["Цветы (51 роза)", "Хромосомы (47 😅)", "Деньги (35 тысяч)"],
        "correct_option": 0
    },
    {
        "question": "🍬 *Мой первый бизнес на Озоне…*\nВсё начиналось с чего-то маленького и душевного.\nС чем он был связан?",
        "options": ["Наборы сладостей", "Игрушки", "Напитки"],
        "correct_option": 0
    },
    {
        "question": "🏥 *Когда ты попала в больницу, ты часто смотрела на один процесс…*\nИ я помню это, потому что тогда особенно переживал за тебя.\nЧто это было?",
        "options": ["Раствор марганца", "Клизма", "Осмотр горла"],
        "correct_option": 0
    },
    {
        "is_riddle": True,
        "riddle_type": "support",
        "riddle_text": "Это не зовут, оно просто рядом.\nНе кричит, но всегда слышит.\nТы не одна. Что это?",
        "riddle_answer": "Поддержка ❤️",
        "video_url": "https://raw.githubusercontent.com/B3KI41/telegram-love-bot/main/hospital_circle.mov",
        "riddle_response": "Что бы ни происходило, ты всегда можешь положиться на меня.\nЯ рядом. Всегда был и буду."
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
