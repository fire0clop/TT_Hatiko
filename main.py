from telebot import TeleBot
from telebot.storage import StateMemoryStorage
import requests
import json


TOKEN_BOT = "6027228281:AAHNU5lgWna1Oi42s9LhUIsOPiQ14oXsP5Q"
TOKEN_API = "e4oEaZY1Kom5OXzybETkMlwjOCy3i8GSCGTHzWrhd4dc563b"
BASE_URL = "https://api.imeicheck.net/v1/checks"

WHITELIST = {123456789, 1212097073} # Это пример айди пользователя


storage = StateMemoryStorage()
bot = TeleBot(token=TOKEN_BOT, state_storage=storage)

def set_default_commands(bot):
    """Функция стандартной команды старт"""
    bot.set_my_commands([
        ('start', 'Запуск бота'),
    ])

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Запрос на Imei"""
    bot.reply_to(message, "Добро пожаловать! Отправьте IMEI для проверки.")

@bot.message_handler(func=lambda message: message.chat.id not in WHITELIST)
def not_authorized(message):
    """Проверка на вайтлист и ошибка"""
    bot.reply_to(message, "У вас нет доступа к этому боту.")

@bot.message_handler(func=lambda message: message.text.isdigit() and len(message.text) in {15, 16})
def check_imei(message):
    """Проверка на вайтлист и текст сообщения + формирование запроса к апи"""
    imei = message.text
    headers = {
        'Authorization': f'Bearer {TOKEN_API}',
        'Content-Type': 'application/json'
    }
    body = json.dumps({
        "deviceId": imei,
        "serviceId": 1
    })

    try:
        response = requests.post(BASE_URL, headers=headers, data=body)
        if response.status_code == 200:
            data = response.json()
            device_info = data.get("properties", {})
            reply = f"Информация об устройстве с IMEI {imei}:\n"
            reply += f"Модель: {device_info.get('deviceName', 'Неизвестно')}\n"
            reply += f"Страна покупки: {device_info.get('purchaseCountry', 'Неизвестно')}\n"
            reply += f"Статус блокировки: {device_info.get('usaBlockStatus', 'Неизвестно')}\n"
        else:
            reply = "Ошибка при запросе к API. Попробуйте позже."
    except Exception:
        reply = "Не удалось получить данные. Проверьте IMEI или попробуйте позже."

    bot.reply_to(message, reply)


if __name__ == "__main__":
    set_default_commands(bot)
    bot.infinity_polling()

