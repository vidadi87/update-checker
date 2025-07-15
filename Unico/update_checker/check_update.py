import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

APP_ID = "com.unico.android"
APP_URL = f"https://play.google.com/store/apps/details?id={APP_ID}&hl=ru"
CHECK_TIMES = ["09:00", "15:00", "21:00"]

BOT_TOKEN = "7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE"
CHAT_ID = "6231070374"

# 👇 Заглушка для тестов: якобы последнее обновление — 15.07.2025
def get_update_date():
    return "15.07.2025"  # ← тут будет парсинг с сайта позже

def get_last_sent_update_date():
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        res = requests.get(url, timeout=10)
        messages = res.json().get("result", [])
        for msg in reversed(messages):
            if "message" in msg and "text" in msg["message"]:
                text = msg["message"]["text"]
                if text.startswith("📲 Обновление приложения"):
                    for line in text.splitlines():
                        if line.startswith("Дата обновления: "):
                            return line.replace("Дата обновления: ", "").strip()
        return None
    except Exception as e:
        print("Ошибка при получении последней отправленной даты из Telegram:", e)
        return None

def send_telegram_message(update_date):
    text = (
        f"📲 Обновление приложения в Google Play!\n"
        f"Дата обновления: {update_date}\n"
        f"Скачать: https://play.google.com/store/apps/details?id={APP_ID}&hl=ru"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=data)
        print("Уведомление отправлено:", response.status_code)
    except Exception as e:
        print("Ошибка при отправке Telegram-сообщения:", e)

def should_check_now():
    now = datetime.now().strftime("%H:%M")
    return now in CHECK_TIMES

print("Скрипт запущен. Ожидаю время проверки...")

while True:
    if should_check_now():
        update_date = get_update_date()
        last_sent = get_last_sent_update_date()
        print(f"Проверка даты: обновление {update_date}, последняя отправка {last_sent}")
        if update_date != last_sent:
            send_telegram_message(update_date)
        else:
            print("Дата уже была отправлена ранее — уведомление не нужно.")
        time.sleep(60)
    else:
        time.sleep(20)
