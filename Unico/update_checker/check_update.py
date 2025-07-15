import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import telebot

# === Настройки ===
BOT_TOKEN = '7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE'
CHAT_ID = '6231070374'  # твой user_id из Telegram
PACKAGE_NAME = 'com.unico.android'
GOOGLE_PLAY_URL = f'https://play.google.com/store/apps/details?id={PACKAGE_NAME}&hl=ru'

bot = telebot.TeleBot(BOT_TOKEN)


# === Получение даты обновления из Google Play ===
def get_update_date():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
    }
    response = requests.get(GOOGLE_PLAY_URL, headers=headers)
    if not response.ok:
        print("❌ Не удалось загрузить страницу:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    update_blocks = soup.find_all("div", class_="xg1aie")
    for div in update_blocks:
        if re.search(r'\d{1,2} \S+\. \d{4} г\.', div.text):
            return div.text.strip()

    print("❌ Не удалось найти дату обновления на странице.")
    return None


# === Получение последней отправленной даты из чата Telegram ===
def get_last_notified_date():
    updates = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    ).json()

    messages = updates.get("result", [])
    for msg in reversed(messages):
        text = msg.get("message", {}).get("text", "")
        if "Дата обновления" in text:
            match = re.search(r'Дата обновления: (\d{1,2} \S+\. \d{4} г\.)', text)
            if match:
                return match.group(1)
    return None


# === Отправка уведомления в Telegram ===
def send_notification(update_date):
    message = (
        "📲 Обнаружено обновление приложения в Google Play!\n"
        f"Дата обновления: {update_date}\n\n"
        f"🔗 Скачать: {GOOGLE_PLAY_URL}"
    )
    bot.send_message(CHAT_ID, message)


# === Основной скрипт ===
def main():
    print("Скрипт запущен. Выполняю проверку обновления...")

    current_update_date = get_update_date()
    if not current_update_date:
        print("❌ Не удалось получить дату обновления.")
        return

    last_notified_date = get_last_notified_date()
    print(f"Текущая дата обновления: {current_update_date}, Последняя отправленная: {last_notified_date}")

    if current_update_date != last_notified_date:
        send_notification(current_update_date)
        print("✅ Уведомление отправлено.")
    else:
        print("ℹ️ Обновлений не обнаружено.")

if __name__ == '__main__':
    main()
