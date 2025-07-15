import requests
from bs4 import BeautifulSoup
from datetime import datetime

APP_ID = "com.unico.android"
APP_URL = f"https://play.google.com/store/apps/details?id={APP_ID}&hl=ru"

BOT_TOKEN = "7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE"
CHAT_ID = "6231070374"

# Имитируем старую дату обновления
last_update_date = "30 июн. 2025 г."  # Предыдущая версия
# Имитируем новую дату обновления (как будто сегодня)
mock_update_date = "15 июл. 2025 г."  # Новая дата для теста


def get_app_update_date():
    """
    ⚠️ Возвращает подставную дату обновления для теста
    """
    print("⚠️ Имитация: возвращаем подставную дату обновления.")
    return mock_update_date

    # Для реальной даты — можно раскомментировать:
    # try:
    #     headers = {"User-Agent": "Mozilla/5.0"}
    #     res = requests.get(APP_URL, headers=headers, timeout=10)
    #     soup = BeautifulSoup(res.text, "html.parser")
    #     for span in soup.find_all("span"):
    #         if "Последнее обновление" in span.text:
    #             return span.text.strip()
    #     return None
    # except Exception as e:
    #     print("❌ Ошибка при получении даты обновления:", e)
    #     return None


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


# Выполнить немедленную проверку
print("🚀 Скрипт запущен. Выполняю немедленную проверку...")
check_for_update()
