import requests
from bs4 import BeautifulSoup
import time
import datetime

# === Настройки ===
BOT_TOKEN = '7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE'
CHAT_ID = '6231070374'  # ← твой chat_id из Telegram
PACKAGE_NAME = 'com.unico.android'
GOOGLE_PLAY_URL = f'https://play.google.com/store/apps/details?id={PACKAGE_NAME}&hl=ru'


# === Основные функции ===

def get_update_date():
    try:
        response = requests.get(GOOGLE_PLAY_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        date_element = soup.find('div', class_='xg1aie')
        return date_element.text.strip() if date_element else None
    except Exception as e:
        print(f'Ошибка при получении даты: {e}')
        return None


def get_last_saved_date():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        resp = requests.get(url).json()
        messages = resp.get("result", [])
        for msg in reversed(messages):
            text = msg.get("message", {}).get("text", "")
            if "Последняя известная дата обновления:" in text:
                return text.split("Последняя известная дата обновления:")[-1].strip()
    except Exception as e:
        print(f'Ошибка при получении истории сообщений: {e}')
    return None


def send_notification(new_date):
    message = f"📦 Обновление найдено!\nДата обновления: {new_date}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

    # Сохраняем дату в чате, чтобы не отправлять дубли
    log_message = f"Последняя известная дата обновления: {new_date}"
    requests.post(url, data={"chat_id": CHAT_ID, "text": log_message})


def check_and_notify():
    print("Скрипт запущен. Выполняю проверку...")
    current_date = get_update_date()
    if not current_date:
        print("❌ Не удалось найти дату обновления на странице.")
        return

    last_known_date = get_last_saved_date()
    print(f"Актуальная дата: {current_date} | Последняя сохранённая: {last_known_date}")

    if current_date != last_known_date:
        print("🔔 Найдено обновление. Отправка уведомления...")
        send_notification(current_date)
    else:
        print("ℹ️ Обновлений нет.")


# === Основной цикл — 3 раза в сутки ===

if __name__ == "__main__":
    while True:
        check_and_notify()
        print("⏳ Следующая проверка через 8 часов...\n")
        time.sleep(8 * 60 * 60)  # 8 часов пауза
