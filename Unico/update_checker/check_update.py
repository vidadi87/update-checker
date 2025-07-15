import requests
from bs4 import BeautifulSoup
import time
import datetime
import re

# === Настройки ===
BOT_TOKEN = 'ВАШ_ТОКЕН_БОТА'
CHAT_ID = 'ВАШ_CHAT_ID_ПОЛЬЗОВАТЕЛЯ'
GROUP_CHAT_ID = -1002781665654  # ID вашей Telegram-группы
PACKAGE_NAME = 'com.unico.android'
GOOGLE_PLAY_URL = f'https://play.google.com/store/apps/details?id={PACKAGE_NAME}&hl=ru'

# === Функции ===

def log(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = f"[{timestamp}] {message}"
    print(entry)
    return entry

def get_update_date():
    try:
        response = requests.get(GOOGLE_PLAY_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        date_element = soup.find('div', class_='xg1aie')
        return date_element.text.strip() if date_element else None
    except Exception as e:
        log(f"Ошибка при получении даты: {e}")
        return None

def get_group_description():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    resp = requests.get(url, params={"chat_id": GROUP_CHAT_ID}).json()
    return resp.get("result", {}).get("description", "")

def extract_date_from_description(desc):
    match = re.search(r'\d{1,2} \w{3}\. \d{4} г\.', desc)
    return match.group(0) if match else None

def update_group_description(new_date):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setChatDescription"
    requests.post(url, data={"chat_id": GROUP_CHAT_ID, "description": new_date})

def send_notification(new_date, log_text):
    message = (
        "📦 Обновление найдено!\n"
        f"Дата обновления: {new_date}\n"
        f"Ссылка для скачивания: {GOOGLE_PLAY_URL}"
    )
    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(send_url, data={"chat_id": CHAT_ID, "text": message, "disable_web_page_preview": True})

    # Лог как файл
    send_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {"document": ("last_check_log.txt", log_text)}
    requests.post(send_file_url, data={"chat_id": CHAT_ID}, files=files)

def check_and_notify():
    log_entries = []
    log_entries.append(log("Проверка обновлений..."))

    play_date = get_update_date()
    group_description = get_group_description()
    saved_date = extract_date_from_description(group_description)

    log_entries.append(log(f"Дата на Google Play: {play_date} | Дата в описании группы: {saved_date}"))

    if not play_date:
        log_entries.append(log("❌ Не удалось получить дату обновления."))
        return

    if play_date != saved_date:
        log_entries.append(log("🔔 Найдено обновление или дата отсутствует. Отправка уведомления..."))
        update_group_description(play_date)
        send_notification(play_date, "\n".join(log_entries))
    else:
        log_entries.append(log("ℹ️ Обновлений нет."))

# === Основной цикл: каждые 30 минут ===

if __name__ == "__main__":
    while True:
        check_and_notify()
        time.sleep(30 * 60)  # 30 минут
