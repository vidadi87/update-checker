import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# === Настройки ===
BOT_TOKEN = '7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE'
USER_CHAT_ID = '6231070374'  # Telegram ID пользователя для уведомлений
GROUP_CHAT_ID = '-1002781665654'  # Telegram-группа для хранения даты
PACKAGE_NAME = 'com.unico.android'
GOOGLE_PLAY_URL = f'https://play.google.com/store/apps/details?id={PACKAGE_NAME}&hl=ru'

# === Получение даты из Google Play ===
def get_update_date():
    try:
        response = requests.get(GOOGLE_PLAY_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        date_element = soup.find('div', class_='xg1aie')
        return date_element.text.strip() if date_element else None
    except Exception as e:
        return f"[ОШИБКА] Ошибка при получении даты: {e}"

# === Получение описания группы (для чтения даты) ===
def get_group_description():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    params = {"chat_id": GROUP_CHAT_ID}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        return data['result'].get('description', '')
    except Exception as e:
        return f"[ОШИБКА] Ошибка при получении описания группы: {e}"

# === Обновление описания группы (с новой датой) ===
def update_group_description(new_date):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setChatDescription"
    payload = {
        "chat_id": GROUP_CHAT_ID,
        "description": new_date  # Без префикса
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"[ОШИБКА] Ошибка при обновлении описания группы: {e}")

# === Отправка уведомления пользователю + лог как файл ===
def send_notification(update_date, log_lines):
    message = (
        f"\U0001F4E6 Обновление найдено!\n"
        f"Дата обновления: {update_date}\n"
        f"Ссылка для скачивания: {GOOGLE_PLAY_URL}"
    )

    # Отправка сообщения
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": USER_CHAT_ID, "text": message, "disable_web_page_preview": True}
    )

    # Создание и отправка лог-файла
    log_path = "latest_update_log.txt"
    with open(log_path, "w", encoding="utf-8") as file:
        for line in log_lines:
            file.write(line + "\n")

    with open(log_path, "rb") as file:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
            data={"chat_id": USER_CHAT_ID},
            files={"document": file}
        )

# === Основная логика ===
def check_for_updates():
    log = []
    now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log.append(f"{now} Проверка обновлений...")

    google_play_date = get_update_date()
    group_description = get_group_description()

    log.append(f"{now} Дата на Google Play: {google_play_date} | Дата в описании группы: {group_description}")

    if not google_play_date or 'ОШИБКА' in google_play_date:
        log.append(f"{now} Ошибка при получении даты, пропуск.")
        return

    if google_play_date != group_description:
        log.append(f"{now} Уведомление отправлено пользователю")
        send_notification(google_play_date, log)
        update_group_description(google_play_date)
    else:
        log.append(f"{now} Обновлений нет.")

# === Запуск цикла проверки ===
if __name__ == "__main__":
    while True:
        check_for_updates()
        time.sleep(15)  # Проверка каждые 15 секунд