from datetime import datetime
import requests

BOT_TOKEN = "7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE"
CHAT_ID = "6231070374"
APP_URL = "https://play.google.com/store/apps/details?id=com.unico.android&hl=ru"

# Имитация: якобы из Telegram бот прочитал, что последнее обновление было 14 июля
def get_last_known_date_from_telegram():
    return "14 июл. 2025 г."

# Имитация: якобы на Google Play указано обновление от 15 июля
def get_current_update_date():
    return "15 июл. 2025 г."

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": False}
    try:
        response = requests.post(url, data=data)
        print("Уведомление отправлено:", response.status_code)
    except Exception as e:
        print("Ошибка при отправке Telegram-сообщения:", e)

def check_update():
    print("Скрипт запущен. Выполняю немедленную проверку...")

    last_known_date = get_last_known_date_from_telegram()
    current_date = get_current_update_date()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Текущая дата обновления: {current_date}, Предыдущая: {last_known_date}")

    if current_date and current_date != last_known_date:
        text = (
            "📲 Обнаружено обновление приложения в Google Play!\n"
            f"Дата обновления: {current_date}\n"
            f"🔗 Скачать: {APP_URL}"
        )
        send_telegram_message(text)
    else:
        print("Обновление не обнаружено.")

check_update()
