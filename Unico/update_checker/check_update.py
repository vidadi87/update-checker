import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import tempfile

# === Настройки ===
BOT_TOKEN = '7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE'
BOT_CHAT_ID = '6231070374'  # Получатель уведомлений (бот)
GROUP_CHAT_ID = '-1002781665654'  # Группа, где храним дату в описании
PACKAGE_NAME = 'com.unico.android'
GOOGLE_PLAY_URL = f'https://play.google.com/store/apps/details?id={PACKAGE_NAME}&hl=ru'


# === Вспомогательные функции ===
def normalize_date(date_str):
    return date_str.replace('\u202f', ' ').replace('\xa0', ' ').strip()


def get_update_date():
    try:
        response = requests.get(GOOGLE_PLAY_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        date_element = soup.find('div', class_='xg1aie')
        return date_element.text.strip() if date_element else None
    except Exception as e:
        return None


def get_group_description():
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat?chat_id={GROUP_CHAT_ID}"
        resp = requests.get(url).json()
        return resp.get("result", {}).get("description", "")
    except Exception:
        return ""


def set_group_description(new_text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setChatDescription"
    data = {
        "chat_id": GROUP_CHAT_ID,
        "description": new_text
    }
    requests.post(url, data=data)


def send_update_notification(date_str, log_text):
    message = (
        f"📦 Обновление найдено!\n"
        f"Дата обновления: {date_str}\n"
        f"Ссылка для скачивания: {GOOGLE_PLAY_URL}"
    )

    send_text_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    send_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

    # Отправка текста
    requests.post(send_text_url, data={
        "chat_id": BOT_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    })

    # Отправка лога последнего запуска
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt") as f:
        f.write(log_text)
        f.flush()
        with open(f.name, "rb") as file_data:
            requests.post(send_file_url, data={"chat_id": BOT_CHAT_ID}, files={"document": file_data})


# === Основной цикл ===
if __name__ == "__main__":
    while True:
        log_lines = []
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        log_lines.append(f"{timestamp} Проверка обновлений...")

        new_date = get_update_date()
        group_desc = get_group_description()

        if not new_date:
            log_lines.append(f"{timestamp} ❌ Не удалось получить дату обновления.")
        else:
            group_date = group_desc.strip()
            norm_new = normalize_date(new_date)
            norm_group = normalize_date(group_date)

            log_lines.append(f"{timestamp} Дата на Google Play: {norm_new} | Дата в описании группы: {norm_group}")

            if norm_new != norm_group:
                send_update_notification(norm_new, "\n".join(log_lines))
                set_group_description(norm_new)
                log_lines.append(f"{timestamp} Уведомление отправлено пользователю")
            else:
                log_lines.append(f"{timestamp} Обновлений нет.")

        time.sleep(15)
