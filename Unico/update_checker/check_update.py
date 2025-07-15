import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

print("Скрипт запущен. Выполняю немедленную проверку...")

APP_ID = "com.unico.android"
APP_URL = f"https://play.google.com/store/apps/details?id={APP_ID}&hl=ru"
BOT_TOKEN = "7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE"
CHAT_ID = "6231070374"

# Подставная дата для теста: имитируем, что приложение обновлено сегодня
def get_fake_update_date():
    return datetime.now().strftime("%d %b. %Y г.").replace("Jul", "июл").replace("Jun", "июн")

def get_update_date():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(APP_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        all_divs = soup.find_all("div")
        for div in all_divs:
            if "Последнее обновление" in div.text:
                # return div.find_next_sibling("span").text.strip()
                return get_fake_update_date()  # <== заменить на строку выше после тестов
        return None
    except Exception as e:
        print("Ошибка при получении даты обновления:", e)
        return None

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=data)
        print("Уведомление отправлено:", response.status_code)
    except Exception as e:
        print("Ошибка при отправке Telegram-сообщения:", e)

last_update_date = "30 июн. 2025 г."  # изначально известная дата

def check_update():
    global last_update_date
    current_date = get_update_date()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Текущая дата обновления: {current_date}, Предыдущая: {last_update_date}")

    if current_date and current_date != last_update_date:
        send_telegram_message(
            f"📲 Обнаружено обновление приложения в Google Play!\n"
            f"Дата обновления: {current_date}\n\n"
            f"🔗 Скачать: {APP_URL}"
        )
        last_update_date = current_date
    else:
        print("Обновлений не обнаружено.")

# Запуск сразу
check_update()