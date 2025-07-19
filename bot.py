import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота из BotFather
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_TOKEN not set")
    raise ValueError("TELEGRAM_TOKEN environment variable is not set")
bot = telebot.TeleBot(TOKEN)

# Приветственное сообщение
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

# Ссылки для записи
LINKS = {
    "limassol_individual": "https://2meetup.in/polina-psychologist/meet30",
    "limassol_couple": "https://2meetup.in/polina-psychologist/terapiya-pary",
    "online_individual": "https://2meetup.in/polina-psychologist1/individualnaya-vstrecha-onlajn",
    "online_couple": "https://2meetup.in/polina-psychologist1/meet30"
}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    logger.info(f"Received /start from chat_id: {message.chat.id}")
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📍 В Лимассоле", callback_data="location_limassol"),
        InlineKeyboardButton("💻 Онлайн", callback_data="location_online")
    )
    bot.send_message(message.chat.id, WELCOME_MESSAGE, reply_markup=markup)

# Обработчик выбора локации
@bot.callback_query_handler(func=lambda call: call.data.startswith("location_"))
def handle_location(call):
    logger.info(f"Received location callback: {call.data}")
    location = call.data.split("_")[1]
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
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup
    )

# Обработчик выбора типа сессии
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

# Vercel serverless функция
def handler(event, context):
    logger.info("Received event: %s", event)
    try:
        # Проверяем, что body существует и является строкой или словарем
        body = event.get('body', '')
        if isinstance(body, str):
            body = json.loads(body) if body else {}
        logger.info("Parsed body: %s", body)
        update = telebot.types.Update.de_json(body)
        if update:
            logger.info("Processing update: %s", update)
            bot.process_new_updates([update])
        else:
            logger.warning("No valid update received")
        return {"statusCode": 200, "body": "OK"}
    except Exception as e:
        logger.error("Error processing request: %s", str(e))
        return {"statusCode": 500, "body": str(e)}
