import requests
from bs4 import BeautifulSoup
from datetime import datetime

print("Скрипт запущен. Выполняю немедленную проверку...")

APP_ID = "com.unico.android"
APP_URL = f"https://play.google.com/store/apps/details?id={APP_ID}&hl=ru"

BOT_TOKEN = "7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE"
CHAT_ID = "6231070374"

last_version = None  # Глобальная переменная для отслеживания версии


def get_app_version():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(APP_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        spans = soup.find_all("span")

        for i, span in enumerate(spans):
            if "Текущая версия" in span.text:
                return "1000.000.000"  # Подставная версия для теста
        return None
    except Exception as e:
        print("Ошибка при получении версии:", e)
        return None


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=data)
        print("Уведомление отправлено:", response.status_code)
    except Exception as e:
        print("Ошибка при отправке Telegram-сообщения:", e)


def check_for_update():
    global last_version
    version = get_app_version()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{now}] Получена версия: {version}, Предыдущая: {last_version}")

    if version:
        if last_version is not None and version != last_version:
            print(f"[{now}] Обнаружена новая версия: {version}")
            send_telegram_message(f"📲 Обновление приложения в Google Play!\nНовая версия: {version}")
        else:
            print(f"[{now}] Версия не изменилась: {version}")
        last_version = version
    else:
        print(f"[{now}] Не удалось получить версию.")


# ВРЕМЕННО: запуск проверки сразу, без ожидания времени
check_for_update()