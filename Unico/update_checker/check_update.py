import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

APP_ID = "com.unico.android"
APP_URL = f"https://play.google.com/store/apps/details?id={APP_ID}&hl=ru"

BOT_TOKEN = "7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE"
CHAT_ID = "6231070374"

# Здесь храним последнюю "известную" дату — для теста задаём вручную:
last_update_date = "30 июн. 2025 г."  # Что было "вчера"


def get_app_update_date():
    """
    Парсим HTML и извлекаем дату обновления
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(APP_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        for span in soup.find_all("span"):
            if "Последнее обновление" in span.text:
                # ТЕСТ: подменим дату прямо здесь
                print("⚠️ Имитация: возвращаем подставную дату")
                return "31 июн. 2025 г."

                # Если хочешь реальную дату — раскомментируй:
                # match = re.search(r"(\d{1,2} \w+\. \d{4})", span.text)
                # if match:
                #     return match.group(1)
        return None
    except Exception as e:
        print("❌ Ошибка при получении даты обновления:", e)
        return None


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=data)
        print("✅ Уведомление отправлено:", response.status_code)
    except Exception as e:
        print("❌ Ошибка при отправке Telegram-сообщения:", e)


def check_for_update():
    global last_update_date
    new_date = get_app_update_date()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{now}] Текущая дата обновления: {new_date}, Предыдущая: {last_update_date}")

    if new_date and new_date != last_update_date:
        send_telegram_message(f"📲 Обновление приложения в Google Play!\nДата обновления: {new_date}")
        last_update_date = new_date
    else:
        print("⏳ Обновления не обнаружено.")


# Выполнить проверку сразу (без таймера)
print("🚀 Скрипт запущен. Выполняю немедленную проверку...")
check_for_update()
