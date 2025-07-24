import telebot
import os
from time import sleep

API_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(API_TOKEN)

user_states = {}

questions = [
    {
        "text": "📍 Вопрос 1:\nГде была наша первая встреча?\nа) В парке\nб) У меня дома\nв) У твоего подъезда",
        "correct": "в",
        "after": None
    },
    {
        "text": "📍 Вопрос 2:\nЧто я тебе подарил в тот день?\nа) Браслет\nб) Письмо\nв) Объятие",
        "correct": "в",
        "after": {
            "type": "text",
            "content": "💌 Это и правда было просто объятие... но с огромной теплотой. Я до сих пор это помню 🫂"
        }
    },
    {
        "text": "📍 Вопрос 3:\nЧто я чувствую, когда ты рядом?\nа) Спокойствие\nб) Волнение\nв) Всё сразу",
        "correct": "в",
        "after": {
            "type": "media",
            "media_type": "photo",
            "content": "https://telegra.ph/file/your_image_link.jpg"
        }
    }
]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_states[message.chat.id] = {"step": 0, "score": 0}
    bot.send_message(message.chat.id,
                     "Привет, моя хорошая 💜\nГотова пройти наш тёплый тест?\nНапиши 'Поехали'!")

@bot.message_handler(func=lambda m: m.text.lower() == "поехали")
def start_test(message):
    user_states[message.chat.id]["step"] = 0
    bot.send_message(message.chat.id, questions[0]["text"])

@bot.message_handler(func=lambda m: True)
def handle_answer(message):
    state = user_states.get(message.chat.id)

    if not state:
        bot.send_message(message.chat.id, "Напиши /start, чтобы начать сначала 💬")
        return

    step = state["step"]

    if step >= len(questions):
        bot.send_message(message.chat.id, "Ты уже прошла тест 😊")
        return

    correct = questions[step]["correct"]
    if message.text.strip().lower() == correct:
        state["score"] += 1
        bot.send_message(message.chat.id, "✅ Это правильный ответ!")
    else:
        bot.send_message(message.chat.id, "❌ Не совсем так... Но я всё равно улыбаюсь, ведь ты стараешься 😌")

    after = questions[step].get("after")
    if after:
        if after["type"] == "text":
            bot.send_message(message.chat.id, after["content"])
        elif after["type"] == "media":
            if after["media_type"] == "photo":
                bot.send_photo(message.chat.id, after["content"])

    state["step"] += 1

    if state["step"] < len(questions):
        bot.send_message(message.chat.id, questions[state["step"]]["text"])
    else:
        bot.send_message(
            message.chat.id,
            f"🎉 Тест завершён!\nТы ответила правильно на {state['score']} из {len(questions)} вопросов 💜"
        )
        bot.send_message(
            message.chat.id,
            "🎁 Вот тебе маленький сюрприз: https://t.me/your_gift_link\n\nСпасибо, что прошла — ты для меня всё."
        )

print("Бот запущен...")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Ошибка:", e)
        sleep(5)