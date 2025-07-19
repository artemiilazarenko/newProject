from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import os
import json
import logging
import asyncio
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_TOKEN not set")
    raise ValueValue("TELEGRAM_TOKEN not set")
bot = Bot(token=TOKEN)
dp = Dispatcher()

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

def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📍 В Лимассоле"),
        KeyboardButton("💻 Онлайн"),
        KeyboardButton("Контакты")
    )
    return markup

def get_back_to_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("Вернуться в начало"))
    return markup

@dp.message(commands=['start'])
async def start(message: types.Message):
    logger.info(f"Received /start from chat_id: {message.chat.id}")
    await message.answer(WELCOME_MESSAGE, reply_markup=get_main_menu())
    logger.info(f"Sent welcome to chat_id: {message.chat.id}")

@dp.message(lambda message: message.text in ["📍 В Лимассоле", "💻 Онлайн"])
async def handle_menu(message: types.Message):
    logger.info(f"Received menu choice: {message.text} from chat_id: {message.chat.id}")
    location = "limassol" if message.text == "📍 В Лимассоле" else "online"
    text = (
        "Вы выбрали личную встречу в Лимассоле.\nКакой формат вам подходит?"
        if location == "limassol"
        else "Вы выбрали онлайн-консультацию.\nВыберите формат:"
    )
    inline_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("👤 Индивидуальная", callback_data=f"session_{location}_individual")],
        [InlineKeyboardButton("👥 Парная", callback_data=f"session_{location}_couple")]
    ])
    await message.answer(text, reply_markup=inline_markup)

@dp.message(lambda message: message.text == "Контакты")
async def handle_contacts(message: types.Message):
    await message.answer("Если у вас срочный вопрос — пишите напрямую в Telegram +357 9689 2912. Отвечаю в течение 24 часов.", reply_markup=get_back_to_main_menu())

@dp.message(lambda message: message.text == "Вернуться в начало")
async def back_to_start(message: types.Message):
    await start(message)

@dp.callback_query(lambda call: call.data.startswith("session_"))
async def handle_session(call: types.CallbackQuery):
    logger.info(f"Received session callback: {call.data}")
    _, location, session_type = call.data.split("_")
    key = f"{location}_{session_type}"
    link = LINKS.get(key, "Ссылка не найдена")
    text = f"Вы выбрали {'индивидуальную встречу в Лимассоле' if key == 'limassol_individual' else 'парную терапию в офисе (Лимассол)' if key == 'limassol_couple' else 'индивидуальную онлайн-сессию' if key == 'online_individual' else 'парную онлайн-сессию'}.\n\nЗаписаться можно здесь:\n👉 {link}"
    await call.message.edit_text(text)
    await call.message.answer(" ", reply_markup=get_back_to_main_menu())

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''

@app.route('/', methods=['POST'])
async def webhook():
    logger.info("Received webhook request")
    try:
        body = request.get_data()
        if request.headers.get('X-Vercel-Encoding') == 'base64':
            body = base64.b64decode(body)
        json_string = body.decode('utf-8')
        update = types.Update.de_json(json.loads(json_string))
        await dp.process_update(update)
    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}")
    return '', 200

if __name__ == '__main__':
    app.run(debug=True)
