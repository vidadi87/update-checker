import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

BOT_TOKEN = "7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE"
CHAT_ID = "6231070374"
APP_URL = "https://play.google.com/store/apps/details?id=com.unico.android&hl=ru"

# === Имитация: будто в Telegram сохранено последнее уведомление с такой датой ===
def get_last_known_date_from_telegram():
    return "14 июл. 2025 г."  # ← якобы вчерашняя дата из чата

# === Получаем текущую дату обновления с Google Play ===
def get_current_update_date():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(APP_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        spans = soup.find_all("span")

        for span in spans:
            if "Последнее обновление" in span.text:
                date_span = span.find_next_sibling("span")
                if date_span:
                    return date_span.text.strip()
        return None
    except Exception as e:
        print("Ошибка при получении даты обновления:", e)
        return None

# === Отправка уведомления в Telegram ===
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": False}
    try:
        response = requests.post(url, data=data)
        print("Уведомление отправлено:", response.status_code)
    except Exception as e:
        print("Ошибка при отправке Telegram-сообщения:", e)

# === Основная логика ===
def check_update():
    print("Скрипт запущен. Выполняю немедленную проверку...")

    last_known_date = get_last_known_date_from_telegram()
    current_date = get_current_update_date()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Текущая дата обновления: {current_date}, Предыдущая: {last_known_date}")

    if current_date and current_date != last_known_date:
        text = (
            "📲 Обнаружено обновление приложения в Google Play!\n"
            f"Дата обновления: {current_date}\n"
            f"🔗 Скачать: {APP_URL}"
        )
        send_telegram_message(text)
    else:
        print("Обновление не обнаружено.")

check_update()
