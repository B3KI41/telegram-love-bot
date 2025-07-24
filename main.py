
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = "YOUR_BOT_TOKEN"  # Замените на ваш токен

# Вопросы и загадки
questions = [
    {
        "question": "1. Когда была наша первая встреча?",
        "options": ["15 июня", "30 мая", "22 июля"],
        "correct_option": 0
    },
    {
        "question": "2. Что ты делала, когда впервые пришла ко мне домой?",
        "options": ["Трогала мою голову", "Открыла холодильник", "Смотрела телевизор"],
        "correct_option": 0
    },
    {
        "question": "3. Первое наше совместное мероприятие?",
        "options": ["День Рождение", "Свадьба", "Просто посиделка"],
        "correct_option": 0
    },
    {
        "type": "puzzle",
        "question": "❤️ Загадка про любовь",
        "text": "Оно без слов, но говорит. Без рук — но греет. Без вида — но видно. Что это?",
        "answer": "Любовь",
        "image": "https://raw.githubusercontent.com/B3KI41/telegram-love-bot/main/love_photo_1.png"
    },
    {
        "question": "4. Первый мой подарок для тебя, который я никогда больше никому не дарил?",
        "options": ["Цветы (51 роза)", "Хромосомы (47)", "Деньги (35 тысяч)"],
        "correct_option": 0
    },
    {
        "question": "5. Мой первый бизнес на Ozon был связан с…",
        "options": ["Наборы сладостей", "Игрушки", "Напитки"],
        "correct_option": 0
    },
    {
        "question": "6. Когда ты лежала в больнице, тебе нравилось наблюдать за…",
        "options": ["Раствором марганца", "Клизмой", "Осмотром горла"],
        "correct_option": 0
    },

    {
        "type": "puzzle",
        "question": "🤍 Загадка о поддержке",
        "text": "Я не герой, не волшебник и не спасатель. Но даже в моменты, когда ты одна, я рядом. Был, есть и буду плечом — всегда. За что ты можешь быть спокойна?",
        "answer": "Поддержка",
        "video": "https://raw.githubusercontent.com/B3KI41/telegram-love-bot/main/hospital_circle.mov"
    }
]

# Состояние пользователя
user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_state[update.effective_user.id] = {"q": 0}
    await send_question(update, context)

def get_keyboard(q_index):
    q = questions[q_index]
    if "options" in q:
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"answer:{i}")] for i, opt in enumerate(q["options"])]
    else:
        keyboard = [[InlineKeyboardButton("🔁 Начать заново", callback_data="restart")]]
    if q_index > 0:
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_state.get(user_id, {"q": 0})
    q_index = state["q"]
    q = questions[q_index]

    if "options" in q:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=q["question"], reply_markup=get_keyboard(q_index))
    elif q.get("type") == "puzzle":
        await context.bot.send_message(chat_id=update.effective_chat.id, text=q["text"])
        if "image" in q:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=q["image"])
        elif "video" in q:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=q["video"])
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🔁 Начать заново", reply_markup=get_keyboard(q_index))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    state = user_state.get(user_id, {"q": 0})

    if data.startswith("answer:"):
        selected = int(data.split(":")[1])
        current_q = questions[state["q"]]
        correct = current_q["correct_option"]
        if selected == correct:
            await query.edit_message_text(f"✅ Правильно: {current_q['options'][correct]}")
        else:
            await query.edit_message_text(f"❌ Неправильно. Правильный ответ: {current_q['options'][correct]}")
        state["q"] += 1
        user_state[user_id] = state
        if state["q"] < len(questions):
            await send_question(update, context)
    elif data == "back":
        if state["q"] > 0:
            state["q"] -= 1
            await send_question(update, context)
    elif data == "restart":
        state["q"] = 0
        await send_question(update, context)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.run_polling()
