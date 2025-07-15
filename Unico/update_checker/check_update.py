import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

# === Конфигурация ===
BOT_TOKEN = '7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE'
BOT_CHAT_ID = '6231070374'  # Личный чат
GROUP_CHAT_ID = -1002781665654  # Группа, где хранится дата
PACKAGE_NAME = 'com.unico.android'
GOOGLE_PLAY_URL = f'https://play.google.com/store/apps/details?id={PACKAGE_NAME}&hl=ru'

# === Получение даты из Google Play ===
def get_update_date():
    try:
        r = requests.get(GOOGLE_PLAY_URL, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        date = soup.find('div', class_='xg1aie')
        return date.text.strip() if date else None
    except Exception as e:
        return f'Ошибка: {e}'

# === Получение описания из группы ===
def get_group_description():
    r = requests.get(
        f'https://api.telegram.org/bot{BOT_TOKEN}/getChat',
        params={'chat_id': GROUP_CHAT_ID}
    ).json()
    return r.get('result', {}).get('description')

# === Установка описания в группу ===
def set_group_description(new_date):
    requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/setChatDescription',
        data={'chat_id': GROUP_CHAT_ID, 'description': new_date}
    )

# === Отправка уведомления и логов ===
def send_notification(message, log):
    log_path = '/tmp/update_log.txt'
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(log)

    # отправка уведомления
    requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
        data={
            'chat_id': BOT_CHAT_ID,
            'text': message,
            'disable_web_page_preview': True
        }
    )

    # отправка файла
    with open(log_path, 'rb') as f:
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument',
            data={'chat_id': BOT_CHAT_ID},
            files={'document': f}
        )

    os.remove(log_path)

# === Основной цикл ===
while True:
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update_date = get_update_date()

    if update_date is None or 'Ошибка' in update_date:
        send_notification("⚠️ Не удалось получить дату обновления.", f"[{now}] Ошибка: {update_date}")
    else:
        stored = get_group_description()
        log = f"[{now}] Проверка обновления\nТекущая дата с сайта: {update_date}\nДата в описании группы: {stored or 'нет'}"

        if stored != update_date:
            text = (
                f"📦 Обновление найдено!\n"
                f"Дата обновления: {update_date}\n"
                f"Ссылка для скачивания: {GOOGLE_PLAY_URL}"
            )
            send_notification(text, log)
            set_group_description(update_date)
        else:
            print(f"[{now}] Обновлений нет. Дата: {update_date}")

    time.sleep(15)