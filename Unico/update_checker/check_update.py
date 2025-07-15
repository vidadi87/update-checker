import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

# === Настройки ===
BOT_TOKEN = '7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE'
CHAT_ID = '6231070374'
PACKAGE_NAME = 'com.unico.android'
GOOGLE_PLAY_URL = f'https://play.google.com/store/apps/details?id={PACKAGE_NAME}&hl=ru'
CHECK_INTERVAL_HOURS = 8  # каждые 8 часов = 3 раза в сутки

# Ключевая фраза и формат даты, как на сайте
DATE_LABEL = 'Последнее обновление'
DATE_FORMAT = '%d %b. %Y г.'  # пример: '30 июн. 2025 г.'
LAST_SENT_DATE = None  # Храним последнее значение, чтобы не спамить


def get_update_date():
    try:
        response = requests.get(GOOGLE_PLAY_URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        date_div = soup.find('div', string=DATE_LABEL)
        if date_div:
            date_text = date_div.find_next_sibling('div').text.strip()
            return date_text
        else:
            print("❌ Не удалось найти дату обновления на странице.")
            return None
    except Exception as e:
        print(f"❌ Не удалось получить дату обновления.\nОшибка: {e}")
        return None


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Уведомление отправлено.")
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомления: {e}")


def check_for_update():
    global LAST_SENT_DATE
    print("⚙️ Скрипт запущен. Выполняю проверку обновления...")

    current_date = get_update_date()
    print(f"📅 Текущая дата обновления: {current_date}")

    if current_date:
        if current_date != LAST_SENT_DATE:
            LAST_SENT_DATE = current_date
            message = (
                f"📦 <b>Обнаружено обновление приложения в Google Play!</b>\n"
                f"<b>Дата обновления:</b> {current_date}\n\n"
                f"🔗 <a href=\"{GOOGLE_PLAY_URL}\">Скачать: {GOOGLE_PLAY_URL}</a>"
            )
            send_telegram_message(message)
        else:
            print(f"ℹ️ Последняя известная дата: {LAST_SENT_DATE} (уведомление не отправлено)")
    else:
        print("⚠️ Дата обновления отсутствует.")


# === Запуск цикла ===
if __name__ == '__main__':
    while True:
        check_for_update()
        time.sleep(CHECK_INTERVAL_HOURS * 60 * 60)
