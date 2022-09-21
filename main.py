import telebot
from telebot.types import Message
from keys import BOT_TOKEN, ADMIN_ID
import json


bot_client = telebot.TeleBot(BOT_TOKEN)


@bot_client.message_handler(commands=["start"])
def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username

    with open("users.json", "r") as f:
        data_from_json = json.load(f)

    if user_id not in data_from_json:
        data_from_json[user_id] = {"username": username}

    with open("users.json", "w") as f:
        json.dump(data_from_json, f, indent=4, ensure_ascii=False)

    bot_client.send_message(chat_id=user_id, text=f"Пользователь {username} успешно зарегистрирован")


def handle_ask_me(message: Message):
    bot_client.reply_to(message, "Спасибо, что поделился! Скоро я прочитаю твое сообщение и разберу все возникшие вопросы. Хорошего дня!")


@bot_client.message_handler(commands="ask_me")
def ask_me(message: Message):
    bot_client.reply_to(message, text="Привет!\nКак успехи?\nРешал вчера ЕГЭ?\nКакие трудности возникли?\n---\n"
                                      "Пожалуйста, отправь ответ в одном сообщении боту или же напиши мне лично @yanasirina")
    bot_client.register_next_step_handler(message, callback=handle_ask_me)


bot_client.polling()
