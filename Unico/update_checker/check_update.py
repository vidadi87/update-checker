import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import locale

# Устанавливаем русскую локаль для разбора "июл." и т.д.
locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")

APP_ID = "com.unico.android"
APP_URL = f"https://play.google.com/store/apps/details?id={APP_ID}&hl=ru"
CHECK_TIMES = ["09:00", "15:00", "21:00"]

BOT_TOKEN = "7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE"
CHAT_ID = "6231070374"

last_checked_date = None


def get_app_update_date():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(APP_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        spans = soup.find_all("span")

        for i, span in enumerate(spans):
            if "Последнее обновление" in span.text:
                return spans[i + 1].text.strip()
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


def get_last_sent_update_date():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        res = requests.get(url)
        updates = res.json()["result"]
        for update in reversed(updates):
            message = update.get("message", {})
            text = message.get("text", "")
            if "📲 Обновление приложения" in text:
                lines = text.split("\n")
                for line in lines:
                    if "Дата обновления:" in line:
                        return line.split("Дата обновления:")[-1].strip()
        return None
    except Exception as e:
        print("Ошибка при получении истории из Telegram:", e)
        return None


def should_check_now():
    global last_checked_date
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.date()

    if current_time in CHECK_TIMES:
        if last_checked_date != (current_date, current_time):
            last_checked_date = (current_date, current_time)
            return True
    return False


print("Скрипт запущен. Ожидаю время проверки...")

while True:
    if should_check_now():
        current_update_date = get_app_update_date()
        last_sent_date = get_last_sent_update_date()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{now}] Последняя дата обновления в Google Play: {current_update_date}")
        print(f"[{now}] Последняя отправленная дата: {last_sent_date}")

        if current_update_date and current_update_date != last_sent_date:
            send_telegram_message(
                f"📲 Обновление приложения в Google Play!\n"
                f"Дата обновления: {current_update_date}\n"
                f"https://play.google.com/store/apps/details?id={APP_ID}&hl=ru"
            )
        else:
            print(f"[{now}] Дата не изменилась.")
        time.sleep(60)
    else:
        time.sleep(20)
