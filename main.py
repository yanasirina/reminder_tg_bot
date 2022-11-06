import telebot
from telebot.types import Message
from datetime import datetime, date
from envparse import Env
from clients.telegram_client import TelegramClient
from clients.sqlite3_client import SQLiteClient
from actioners import UserAction
from logging import getLogger, StreamHandler


logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("INFO")

env = Env()
BOT_TOKEN = env.str("BOT_TOKEN")
ADMIN_ID = env.str("ADMIN_ID")
user_act = UserAction(SQLiteClient("users.db"))


class MyBot(telebot.TeleBot):
    def __init__(self, telegram_client: TelegramClient, user_action: UserAction, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.telegram_client = telegram_client
        self.user_action = user_action

    def setup_resources(self):
        self.user_action.setup()

    def shutdown_resources(self):
        self.user_action.shutdown()


tg_client = TelegramClient(token=BOT_TOKEN, base_url="https://api.telegram.org")
bot_client = MyBot(telegram_client=tg_client, token=BOT_TOKEN, user_action=user_act)
bot_client.setup_resources()


@bot_client.message_handler(commands=["start"])
def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id
    create_new_user = False

    user = bot_client.user_action.get_user(user_id=user_id)
    if not user:
        bot_client.user_action.create_user(user_id=user_id, username=username, chat_id=chat_id)
        create_new_user = True

    reply = f"Вы {'уже ' if not create_new_user else ''}зарегистрированы: {username}.\n" \
            f"Ваш id: {user_id}."
    bot_client.reply_to(message=message, text=reply)


def handle_ask_me(message: Message):
    bot_client.user_action.update_date(user_id=str(message.from_user.id), updated_date=date.today())
    bot_client.send_message(chat_id=ADMIN_ID, text=f"Пользователь: {message.from_user.id} {message.from_user.username}"
                                                   f"\n\nСообщение: {message.text}"
                                                   f"\n\nДата: {date.today()}")
    bot_client.reply_to(message, "Спасибо, что поделился! Скоро я прочитаю твое сообщение и разберу все возникшие вопросы. Хорошего дня!")


@bot_client.message_handler(commands="ask_me")
def ask_me(message: Message):
    bot_client.reply_to(message, text="Привет!\nКак успехи?\nРешал вчера ЕГЭ?\nКакие трудности возникли?\n---\n"
                                      "Пожалуйста, отправь ответ в одном сообщении боту или же напиши мне лично @yanasirina")
    bot_client.register_next_step_handler(message, callback=handle_ask_me)


while True:
    try:
        bot_client.setup_resources()
        bot_client.polling()
    except Exception as error:
        txt = f"{error.__class__}\n{error}\n\n{datetime.now()}"
        bot_client.telegram_client.post(method="sendMessage", params={"text": txt,
                                                                      "chat_id": ADMIN_ID})
        logger.error(txt)
        bot_client.shutdown_resources()
