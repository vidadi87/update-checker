import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

# === Настройки ===
BOT_TOKEN = '7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE'
BOT_CHAT_ID = '6231070374'  # Личный бот-чат (только тебе)
GROUP_CHAT_ID = '-1002781665654'
GOOGLE_PLAY_URL = 'https://play.google.com/store/apps/details?id=com.unico.android&hl=ru'

# === Вспомогательные функции ===

def get_update_date():
    try:
        response = requests.get(GOOGLE_PLAY_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        date_element = soup.find('div', class_='xg1aie')
        return date_element.text.strip() if date_element else None
    except Exception as e:
        return f'Ошибка при получении даты: {e}'

def get_group_description():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    params = {"chat_id": GROUP_CHAT_ID}
    response = requests.get(url, params=params).json()
    return response.get("result", {}).get("description", "")

def update_group_description(new_date):
    full_desc = f"Последняя дата обновления: {new_date}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setChatDescription"
    params = {"chat_id": GROUP_CHAT_ID, "description": full_desc}
    requests.post(url, data=params)

def send_text_and_log_to_bot(date_text, log_content):
    message = (
        f"📦 Обновление найдено!\n"
        f"Дата обновления: {date_text}\n"
        f"Ссылка для скачивания: {GOOGLE_PLAY_URL}"
    )

    # Отправка текста
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": BOT_CHAT_ID,
            "text": message,
            "disable_web_page_preview": True
        }
    )

    # Запись лог-файла
    log_filename = "update_log.txt"
    with open(log_filename, "w", encoding="utf-8") as f:
        f.write(log_content)

    # Отправка файла
    with open(log_filename, "rb") as file:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
            data={"chat_id": BOT_CHAT_ID},
            files={"document": (log_filename, file)}
        )

    os.remove(log_filename)  # Удалить файл после отправки

# === Основной процесс ===

def check_and_notify():
    log = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.append(f"[{now}] Скрипт запущен. Проверка обновлений...")

    current_date = get_update_date()
    if not current_date or "Ошибка" in current_date:
        log.append(f"[{now}] ❌ {current_date}")
        return

    log.append(f"[{now}] Текущая дата обновления на Google Play: {current_date}")

    group_desc = get_group_description()
    last_known_date = ""
    prefix = "Последняя дата обновления: "
    if prefix in group_desc:
        last_known_date = group_desc.split(prefix)[-1].strip()

    log.append(f"[{now}] Последняя сохранённая дата в описании группы: {last_known_date or 'не найдена'}")

    if current_date != last_known_date:
        log.append(f"[{now}] 🔔 Найдено обновление! Отправка уведомления и обновление описания группы...")
        update_group_description(current_date)
        send_text_and_log_to_bot(current_date, "\n".join(log))
    else:
        log.append(f"[{now}] ℹ️ Дата не изменилась. Уведомление не отправлено.")

# === Цикл проверки каждые 15 секунд ===

while True:
    check_and_notify()
    time.sleep(15)
