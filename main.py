import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from time import sleep

API_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

user_states = {}

# ===== ВОПРОСЫ + ЗАГАДКА =====
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

# ========== СТАРТ ==========

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

# ========== ВОПРОСЫ ==========

def send_question(chat_id, step):
    q = questions[step]
    markup = InlineKeyboardMarkup()
    for opt in q["options"]:
        markup.add(InlineKeyboardButton(opt, callback_data=f"answer:{opt}"))

    # Кнопка "Назад"
    if step > 0:
        markup.add(InlineKeyboardButton("⬅️ Назад", callback_data="go_back"))
    bot.send_message(chat_id, q["text"], reply_markup=markup)

# ========== ОТВЕТЫ ==========

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
        elif after["type"] == "media":
            if after["media_type"] == "photo":
                bot.send_photo(chat_id, after["content"], caption=after.get("caption", ""))
            elif after["media_type"] == "video":
                bot.send_video(chat_id, after["content"])

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
            "🎁 Хочешь пройти тест ещё раз?",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("🔁 Начать заново", callback_data="start_test")
            )
        )

# ========== НАЗАД ==========

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

# ========== ЗАПУСК ==========

print("Бот запущен...")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Ошибка:", e)
        sleep(5)
