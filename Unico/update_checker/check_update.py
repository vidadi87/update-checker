import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# === Настройки ===
BOT_TOKEN = '7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE'
CHAT_ID = '6231070374'  # Telegram bot chat (user) ID
GROUP_ID = -1002781665654  # ID группы для хранения даты
PACKAGE_NAME = 'com.unico.android'
GOOGLE_PLAY_URL = f'https://play.google.com/store/apps/details?id={PACKAGE_NAME}&hl=ru'
LOG_FILE_NAME = 'update_log.txt'


# === Функции ===

def log_event(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE_NAME, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] {message}\n')


def get_update_date():
    try:
        response = requests.get(GOOGLE_PLAY_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        date_element = soup.find('div', class_='xg1aie')
        return date_element.text.strip() if date_element else None
    except Exception as e:
        log_event(f'Ошибка при получении даты: {e}')
        return None


def get_group_description():
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getChat?chat_id={GROUP_ID}'
    try:
        resp = requests.get(url).json()
        return resp.get('result', {}).get('description', '')
    except Exception as e:
        log_event(f'Ошибка при получении описания группы: {e}')
        return ''


def set_group_description(new_date):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/setChatDescription'
    data = {
        'chat_id': GROUP_ID,
        'description': new_date  # без префикса
    }
    try:
        requests.post(url, data=data)
        log_event(f'Описание группы обновлено на: {new_date}')
    except Exception as e:
        log_event(f'Ошибка при установке описания группы: {e}')


def send_notification(date):
    # Сообщение
    message = (
        f"📦 Обновление найдено!\n"
        f"Дата обновления: {date}\n"
        f"Ссылка для скачивания: {GOOGLE_PLAY_URL}"
    )
    msg_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    msg_data = {
        'chat_id': CHAT_ID,
        'text': message,
        'disable_web_page_preview': True
    }
    # Отправка уведомления
    requests.post(msg_url, data=msg_data)
    log_event('Уведомление отправлено пользователю')

    # Отправка лога
    file_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument'
    with open(LOG_FILE_NAME, 'rb') as file:
        requests.post(file_url, files={'document': file}, data={'chat_id': CHAT_ID})
    log_event('Файл лога отправлен пользователю')


def check_and_notify():
    log_event('Проверка обновлений...')
    current_date = get_update_date()
    if not current_date:
        log_event('Дата обновления не найдена на странице.')
        return

    group_description = get_group_description()
    log_event(f'Дата на Google Play: {current_date} | Дата в описании группы: {group_description}')

    if current_date != group_description:
        send_notification(current_date)
        set_group_description(current_date)
    else:
        log_event('Обновлений не обнаружено.')


# === Цикл с интервалом 15 секунд ===

if __name__ == "__main__":
    while True:
        check_and_notify()
        time.sleep(15)
