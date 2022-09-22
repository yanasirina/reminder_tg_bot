from json import JSONDecodeError
import telebot
from telebot.types import Message
import json
import requests
from datetime import datetime
from envparse import Env


class TelegramClient:
    def __init__(self, token: str, base_url: str):
        self.token = token
        self.base_url = base_url

    def prepare_url(self, method: str):
        result_url = f"{self.base_url}/bot{self.token}/"
        if method is not None:
            result_url += method
        return result_url

    def post(self, method: str = None, params: dict = None, data: dict = None):
        url = self.prepare_url(method)
        resp = requests.post(url, params=params, data=data)
        return resp.json()


env = Env()
BOT_TOKEN = env.str("BOT_TOKEN")
ADMIN_ID = env.str("ADMIN_ID")

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


while True:
    try:
        bot_client.polling()
    except Exception as error:
        # bot_client.send_message(chat_id=ADMIN_ID, text=f"Ошибка {error}")
        requests.post(f"https://api.telegram.org/bot5413371958:AAFQNG8RE8IT5RKAqaDpPS1Yc_3b6IVm2r0/"
                      f"sendMessage?chat_id=284868574&text={error.__class__}\n{error}\n\n{datetime.now()}")
