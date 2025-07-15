import requests
from bs4 import BeautifulSoup
import time

# === Настройки ===
BOT_TOKEN = '7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE'
CHAT_ID = '6231070374'  # ЛС пользователя
GROUP_CHAT_ID = -1002781665654  # ID группы (для хранения даты)
GOOGLE_PLAY_URL = 'https://play.google.com/store/apps/details?id=com.unico.android&hl=ru'

# === Получение даты обновления из Google Play ===
def get_update_date():
    try:
        response = requests.get(GOOGLE_PLAY_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        date_element = soup.find('div', class_='xg1aie')
        return date_element.text.strip() if date_element else None
    except Exception as e:
        print(f"[Ошибка] Не удалось получить дату обновления: {e}")
        return None

# === Получение текущего описания группы ===
def get_group_description():
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
        resp = requests.get(url, params={"chat_id": GROUP_CHAT_ID}).json()
        return resp.get("result", {}).get("description", "")
    except Exception as e:
        print(f"[Ошибка] Не удалось получить описание группы: {e}")
        return ""

# === Обновление описания группы с новой датой ===
def update_group_description(new_date):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setChatDescription"
        requests.post(url, data={"chat_id": GROUP_CHAT_ID, "description": new_date})
    except Exception as e:
        print(f"[Ошибка] Не удалось обновить описание группы: {e}")

# === Отправка уведомления в Telegram (в ЛС) ===
def send_notification(update_date):
    message = (
        "📦 Обновление найдено!\n"
        f"Дата обновления: {update_date}\n"
        "Ссылка для скачивания: https://play.google.com/store/apps/details?id=com.unico.android&hl=ru"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": True  # ❗️Без превью ссылки
    })

# === Основная проверка и логика ===
def check_update():
    print("[Проверка] Запуск...")
    current_date = get_update_date()
    if not current_date:
        print("⚠️ Дата обновления не найдена.")
        return

    saved_date = get_group_description()
    print(f"📆 Найденная дата: {current_date} | В группе: {saved_date}")

    if saved_date != current_date:
        print("🔔 Обновление обнаружено. Отправка уведомления...")
        send_notification(current_date)
        update_group_description(current_date)
    else:
        print("✅ Обновлений нет.")

# === Бесконечный цикл с проверкой раз в 15 секунд ===
if __name__ == "__main__":
    while True:
        check_update()
        print("⏳ Ждём 15 секунд...\n")
        time.sleep(15)
