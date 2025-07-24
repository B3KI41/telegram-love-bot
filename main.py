import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from time import sleep

API_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

user_states = {}

# Вопросы — добавляй сколько хочешь
questions = [
    {
        "text": "📍 Вопрос 1:\nГде была наша первая встреча?",
        "options": ["В парке", "У меня дома", "У твоего подъезда"],
        "correct": "У твоего подъезда",
        "after": None
    },
    {
        "text": "📍 Вопрос 2:\nЧто я тебе подарил в тот день?",
        "options": ["Браслет", "Письмо", "Объятие"],
        "correct": "Объятие",
        "after": {
            "type": "text",
            "content": "💌 Это было просто объятие, но с огромной теплотой. Я помню это до сих пор."
        }
    },
    {
        "text": "📍 Вопрос 3:\nЧто я чувствую, когда ты рядом?",
        "options": ["Спокойствие", "Волнение", "Всё сразу"],
        "correct": "Всё сразу",
        "after": {
            "type": "media",
            "media_type": "photo",
            "content": "https://telegra.ph/file/your_image_link.jpg"
        }
    }
]

# Сюрпризы между блоками — будут вставляться после каждого N вопросов
surprise_blocks = {
    3: {
        "type": "text",
        "content": "🎁 Маленький бонус за первые 3 вопроса: ты — невероятная. Спасибо, что ты есть 💜"
    },
    6: {
        "type": "media",
        "media_type": "photo",
        "content": "https://telegra.ph/file/another_surprise.jpg"
    }
}

# ========== Старт ==========

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_states[message.chat.id] = {"step": 0, "score": 0, "history": []}
    bot.send_message(
        message.chat.id,
        "Привет, моя хорошая 💜\nГотова пройти наш тёплый тест?\nНажми кнопку ниже, чтобы начать",
        reply_markup=start_keyboard()
    )

def start_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚀 Поехали!", callback_data="start_test"))
    return markup

# ========== Вопросы ==========

def send_question(chat_id, step):
    q = questions[step]
    markup = InlineKeyboardMarkup()
    for opt in q["options"]:
        markup.add(InlineKeyboardButton(opt, callback_data=f"answer:{opt}"))

    # Кнопка "Назад"
    if step > 0:
        markup.add(InlineKeyboardButton("⬅️ Назад", callback_data="go_back"))
    bot.send_message(chat_id, q["text"], reply_markup=markup)

def send_surprise(chat_id, step):
    surprise = surprise_blocks.get(step)
    if not surprise:
        return
    if surprise["type"] == "text":
        bot.send_message(chat_id, surprise["content"])
    elif surprise["type"] == "media":
        if surprise["media_type"] == "photo":
            bot.send_photo(chat_id, surprise["content"])
        elif surprise["media_type"] == "video":
            bot.send_video(chat_id, surprise["content"])

# ========== Ответы ==========

@bot.callback_query_handler(func=lambda call: call.data == "start_test")
def handle_start_test(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_states[chat_id] = {"step": 0, "score": 0, "history": []}
    send_question(chat_id, 0)

@bot.callback_query_handler(func=lambda call: call.data.startswith("answer:"))
def handle_answer(call: CallbackQuery):
    chat_id = call.message.chat.id
    state = user_states.get(chat_id)

    if not state:
        bot.send_message(chat_id, "Напиши /start 💬")
        return

    selected = call.data.split("answer:")[1]
    step = state["step"]
    q = questions[step]

    # очистить inline-кнопки
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)

    # обработка ответа
    state["history"].append(step)
    if selected == q["correct"]:
        state["score"] += 1
        bot.send_message(chat_id, "✅ Это правильный ответ!")
    else:
        bot.send_message(chat_id, "❌ Не совсем так... Но ты всё равно лучшая 💜")

    if q.get("after"):
        after = q["after"]
        if after["type"] == "text":
            bot.send_message(chat_id, after["content"])
        elif


r["type"] == "media":
            if after["media_type"] == "photo":
                bot.send_photo(chat_id, after["content"])

    # сюрпризный блок
    send_surprise(chat_id, step + 1)

    # следующий вопрос
    state["step"] += 1

    if state["step"] < len(questions):
        send_question(chat_id, state["step"])
    else:
        bot.send_message(
            chat_id,
            f"🎉 Тест завершён! Ты ответила правильно на {state['score']} из {len(questions)} 💜"
        )
        bot.send_message(
            chat_id,
            "🎁 Вот твой финальный сюрприз: https://t.me/your_gift_link"
        )
        bot.send_message(
            chat_id,
            "Хочешь пройти ещё раз?",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("🔁 Начать заново", callback_data="start_test")
            )
        )

# ========== Назад ==========

@bot.callback_query_handler(func=lambda call: call.data == "go_back")
def go_back(call: CallbackQuery):
    chat_id = call.message.chat.id
    state = user_states.get(chat_id)
    if state and state["history"]:
        last = state["history"].pop()
        state["step"] = last
        state["score"] = max(0, state["score"] - 1)
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
        send_question(chat_id, state["step"])
    else:
        bot.send_message(chat_id, "Это был самый первый вопрос 🥺")

# ========== Запуск ==========

print("Бот запущен...")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Ошибка:", e)
        sleep(5)
