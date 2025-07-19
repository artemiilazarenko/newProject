from flask import Flask, request, abort
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_TOKEN not set")
    raise ValueError("TELEGRAM_TOKEN environment variable is not set")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

WELCOME_MESSAGE = """
Доброго времени суток! 

Я — Полина Кусова 
Психолог-сексолог | Семейный терапевт | Преподаватель | Основатель Resonance.Lab

Чтобы записаться на консультацию, или узнать подробнее условиях, стоимости, выберете вариант ниже: 

📍 В Лимассоле (офлайн)
💻 Онлайн

Просто нажмите на кнопку ниже — и мы продолжим диалог.

С теплом,
Полина Кусова

P.S. Если у вас срочный вопрос — пишите напрямую в Telegram +357 9689 2912. Отвечаю в течение 24 часов
"""

LINKS = {
    "limassol_individual": "https://2meetup.in/polina-psychologist/meet30",
    "limassol_couple": "https://2meetup.in/polina-psychologist/terapiya-pary",
    "online_individual": "https://2meetup.in/polina-psychologist1/individualnaya-vstrecha-onlajn",
    "online_couple": "https://2meetup.in/polina-psychologist1/meet30"
}

# Функция для создания меню внизу (ReplyKeyboardMarkup)
def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📍 В Лимассоле"),
        KeyboardButton("💻 Онлайн"),
        KeyboardButton("Контакты")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    logger.info(f"Received /start from chat_id: {message.chat.id}")
    bot.send_message(message.chat.id, WELCOME_MESSAGE, reply_markup=get_main_menu())

# Обработчик текстовых сообщений от кнопок меню
@bot.message_handler(func=lambda message: message.text in ["📍 В Лимассоле", "💻 Онлайн"])
def handle_menu(message):
    logger.info(f"Received menu choice: {message.text} from chat_id: {message.chat.id}")
    location = "limassol" if message.text == "📍 В Лимассоле" else "online"
    text = (
        "Вы выбрали личную встречу в Лимассоле.\nКакой формат вам подходит?"
        if location == "limassol"
        else "Вы выбрали онлайн-консультацию.\nВыберите формат:"
    )
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("👤 Индивидуальная", callback_data=f"session_{location}_individual"),
        InlineKeyboardButton("👥 Парная", callback_data=f"session_{location}_couple")
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

# Обработчик для кнопки "Контакты"
@bot.message_handler(func=lambda message: message.text == "Контакты")
def handle_contacts(message):
    bot.send_message(message.chat.id, "Если у вас срочный вопрос — пишите напрямую в Telegram +357 9689 2912. Отвечаю в течение 24 часов.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("session_"))
def handle_session(call):
    logger.info(f"Received session callback: {call.data}")
    _, location, session_type = call.data.split("_")
    key = f"{location}_{session_type}"
    link = LINKS.get(key, "Ссылка не найдена")
    text = (
        f"Вы выбрали {'индивидуальную встречу в Лимассоле' if key == 'limassol_individual' else 'парную терапию в офисе (Лимассол)' if key == 'limassol_couple' else 'индивидуальную онлайн-сессию' if key == 'online_individual' else 'парную онлайн-сессию'}.\n\n"
        f"Записаться можно здесь:\n👉 {link}"
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text
    )

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''

@app.route('/', methods=['POST'])
def webhook():
    logger.info("Received webhook request")
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json.loads(json_string))
        bot.process_new_updates([update])
        return '', 200
    else:
        abort(403)

if __name__ == '__main__':
    app.run(debug=True)
