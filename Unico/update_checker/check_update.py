import requests
from bs4 import BeautifulSoup
import datetime
import re

# === Настройки ===
BOT_TOKEN = "7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE"
CHAT_ID = "6231070374"
GROUP_CHAT_ID = -1002781665654
PACKAGE_NAME = "com.unico.android"
GOOGLE_PLAY_URL = f"https://play.google.com/store/apps/details?id={PACKAGE_NAME}&hl=ru"

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
        return date_element.text.strip().replace('\u202f', ' ').replace('\xa0', ' ') if date_element else None
    except Exception as e:
        return log(f"Ошибка при получении даты: {e}")

def get_group_description():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    resp = requests.get(url, params={"chat_id": GROUP_CHAT_ID}).json()
    return resp.get("result", {}).get("description", "")

def extract_date_from_description(desc):
    match = re.search(r'\d{1,2} \w+\. \d{4} г\.', desc)
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

    # Лог текущего запуска
    send_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    files = {"document": ("update_log.txt", log_text)}
    requests.post(send_file_url, data={"chat_id": CHAT_ID}, files=files)

def check_and_notify():
    log_entries = []
    log_entries.append(log("Проверка обновлений..."))

    play_date = get_update_date()
    if not play_date:
        log_entries.append(log("❌ Не удалось получить дату обновления."))
        return

    group_desc = get_group_description()
    saved_date = extract_date_from_description(group_desc)

    # Преобразование пробелов
    play_date_clean = play_date.replace('\u202f', ' ').replace('\xa0', ' ')
    saved_date_clean = saved_date.replace('\u202f', ' ').replace('\xa0', ' ') if saved_date else None

    log_entries.append(log(f"Дата на Google Play: {play_date_clean} | Дата в описании группы: {saved_date_clean}"))

    if play_date_clean != saved_date_clean:
        log_entries.append(log("🔔 Найдено обновление или дата отсутствует. Отправка уведомления..."))
        update_group_description(play_date_clean)
        send_notification(play_date_clean, "\n".join(log_entries))
    else:
        log_entries.append(log("ℹ️ Обновлений нет."))

if __name__ == "__main__":
    check_and_notify()