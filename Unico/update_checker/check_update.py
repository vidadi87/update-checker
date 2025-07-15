import requests
from bs4 import BeautifulSoup
import time

# === Настройки ===
BOT_TOKEN = '7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE'
CHAT_ID = '6231070374'  # Telegram-пользователь для уведомлений
GROUP_CHAT_ID = '-1002781665654'  # Telegram-группа для хранения даты
PACKAGE_NAME = 'com.unico.android'
GOOGLE_PLAY_URL = f'https://play.google.com/store/apps/details?id={PACKAGE_NAME}&hl=ru'

# === Получение даты обновления из Google Play ===
def get_update_date():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(GOOGLE_PLAY_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        date_element = soup.find('div', class_='xg1aie')
        return date_element.text.strip() if date_element else None
    except Exception as e:
        print(f'Ошибка при получении даты обновления: {e}')
        return None

# === Получение текущего описания группы ===
def get_group_description():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
    params = {"chat_id": GROUP_CHAT_ID}
    try:
        response = requests.get(url, params=params).json()
        return response.get("result", {}).get("description", "")
    except Exception as e:
        print(f'Ошибка при получении описания группы: {e}')
        return ""

# === Обновление описания группы с новой датой ===
def set_group_description(new_date):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setChatDescription"
    params = {
        "chat_id": GROUP_CHAT_ID,
        "description": f"Последняя дата обновления: {new_date}"
    }
    try:
        response = requests.post(url, params=params)
        if response.ok:
            print("Описание группы успешно обновлено.")
        else:
            print("Не удалось обновить описание группы.")
    except Exception as e:
        print(f'Ошибка при обновлении описания группы: {e}')

# === Отправка уведомления в Telegram (личка) ===
def send_notification(new_date):
    message = f"📦 Обновление найдено!\nДата обновления: {new_date}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.ok:
            print("✅ Уведомление отправлено.")
        else:
            print("❌ Ошибка при отправке уведомления.")
    except Exception as e:
        print(f'Ошибка при отправке уведомления: {e}')

# === Основная логика ===
def check_for_update():
    print("Запуск проверки обновления...")
    current_date = get_update_date()
    if not current_date:
        print("❌ Не удалось получить дату обновления.")
        return

    group_description = get_group_description()
    if current_date not in group_description:
        print("🔔 Обнаружена новая дата. Отправляем уведомление...")
        send_notification(current_date)
        set_group_description(current_date)
    else:
        print("ℹ️ Новых обновлений нет.")

# === Запуск каждый час ===
if __name__ == "__main__":
    while True:
        check_for_update()
        print("⏳ Следующая проверка через 1 час...\n")
        time.sleep(60 * 60)
