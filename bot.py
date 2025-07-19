import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# Токен бота из BotFather
TOKEN = os.getenv("TELEGRAM_TOKEN")
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
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📍 В Лимассоле", callback_data="location_limassol"),
        InlineKeyboardButton("💻 Онлайн", callback_data="location_online")
    )
    bot.send_message(message.chat.id, WELCOME_MESSAGE, reply_markup=markup)

# Обработчик выбора локации
@bot.callback_query_handler(func=lambda call: call.data.startswith("location_"))
def handle_location(call):
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

# Для Vercel: обработчик вебхука
def handler(event, context):
    update = telebot.types.Update.de_json(event['body'])
    bot.process_new_updates([update])
    return {"statusCode": 200}
