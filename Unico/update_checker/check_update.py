import datetime
import os
import re
import socket
import sys

import requests
from bs4 import BeautifulSoup
from pytz import timezone

# === Настройки ===
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7670367239:AAGYKkgtSmCeejxxAnwLV9R_BgG9um_-ymE")
CHAT_ID = os.environ.get("CHAT_ID", "6231070374")
GROUP_CHAT_ID = os.environ.get("GROUP_CHAT_ID", "-1002781665654")
PACKAGE_NAME = "com.unico.android"
GOOGLE_PLAY_URL = f"https://play.google.com/store/apps/details?id={PACKAGE_NAME}&hl=ru&gl=KZ"

TZ = timezone("Asia/Almaty")
MONTHS_IN = {"янв": 1, "фев": 2, "мар": 3, "апр": 4, "мая": 5, "июн": 6,
             "июл": 7, "авг": 8, "сен": 9, "окт": 10, "ноя": 11, "дек": 12}
MONTHS_OUT = ["янв.", "февр.", "мар.", "апр.", "мая", "июн.",
              "июл.", "авг.", "сент.", "окт.", "нояб.", "дек."]

LOG = []


# === Вспомогательное ===
def now_local():
    return datetime.datetime.now(TZ)


def log(message):
    entry = f"[{now_local():%Y-%m-%d %H:%M:%S}] {message}"
    print(entry, flush=True)
    LOG.append(entry)
    return entry


def safe(err):
    """Текст ошибки без токена бота (requests кладёт URL с токеном в сообщение)."""
    text = str(err)
    return text.replace(BOT_TOKEN, "***") if BOT_TOKEN else text


def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def parse_ru_date(text):
    m = re.search(r"(\d{1,2})\s+([а-яё]+)\.?\s+(\d{4})", (text or "").lower())
    if not m:
        return None
    day, month, year = m.groups()
    for prefix, number in MONTHS_IN.items():
        if month.startswith(prefix):
            try:
                return datetime.date(int(year), number, int(day))
            except ValueError:
                return None
    return None


# === Получение данных с Google Play ===
def fetch_via_library():
    """Точное время и версия. Не зависит от часового пояса, поэтому нет скачков 14/15."""
    try:
        from google_play_scraper import app
    except ImportError:
        return None
    socket.setdefaulttimeout(20)
    info = app(PACKAGE_NAME, lang="ru", country="kz")
    ts = info.get("updated")
    if not isinstance(ts, (int, float)) or ts <= 0:
        return None
    return {"ts": int(ts), "version": info.get("version") or None, "date_text": None}


def fetch_via_html():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9",
    }
    try:
        resp = requests.get(GOOGLE_PLAY_URL, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        log(f"Ошибка при получении страницы: {safe(e)}")
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    text = None
    element = soup.find("div", class_="xg1aie")
    if element:
        text = clean(element.get_text())
    if not parse_ru_date(text):
        # Запасной поиск по подписи, если Google сменил обфусцированный класс
        label = soup.find(string=re.compile("Последнее обновление"))
        found = label.find_next(string=re.compile(r"\d{1,2}\s+[а-яёА-ЯЁ]+\.?\s+\d{4}")) if label else None
        text = clean(found) if found else None
    if not parse_ru_date(text):
        return None
    return {"ts": None, "version": None, "date_text": text}


def fetch_observation():
    """Возвращает (наблюдение, источник). Сначала библиотека, при сбое HTML."""
    try:
        obs = fetch_via_library()
        if obs:
            return obs, "library"
    except Exception as e:
        log(f"Библиотека не отдала данные, перехожу на HTML: {safe(e)}")
    obs = fetch_via_html()
    return (obs, "html") if obs else (None, None)


def describe(obs):
    """Текст вида "15 окт. 2026 г. 12:34, версия 1.2.3". Он же хранится в описании группы."""
    if obs.get("ts"):
        dt = datetime.datetime.fromtimestamp(obs["ts"], TZ)
        text = f"{dt.day} {MONTHS_OUT[dt.month - 1]} {dt.year} г. {dt:%H:%M}"
    else:
        text = obs["date_text"]
    if obs.get("version"):
        text += f", версия {obs['version']}"
    return text


# === Сравнение ===
def fields(text):
    """Разбор текста на (дата, время, версия). Неизвестное поле равно None."""
    text = clean(text)
    time_m = re.search(r"\b(\d{2}:\d{2})\b", text)
    ver_m = re.search(r"версия (\S+)", text)
    return {"date": parse_ru_date(text), "time": time_m.group(1) if time_m else None,
            "version": ver_m.group(1) if ver_m else None, "raw": text}


def differs(new, old):
    """Различие есть, только если поле известно с обеих сторон и не совпадает."""
    if new["date"] is None or old["date"] is None:
        return new["raw"] != old["raw"]
    return any(new[k] is not None and old[k] is not None and new[k] != old[k]
               for k in ("date", "time", "version"))


def classify(new, old, today):
    if new["date"] is None or old["date"] is None:
        kind = "changed"
    elif new["date"] > old["date"]:
        kind = "new_release"
    elif new["date"] < old["date"]:
        kind = "earlier_date"
    elif new["time"] and old["time"] and new["time"] != old["time"]:
        kind = "same_day_newer" if new["time"] > old["time"] else "earlier_date"
    else:
        kind = "changed"
    lag = (today - new["date"]).days if new["date"] else None
    return {"kind": kind, "old": old["raw"] or "нет", "new": new["raw"], "lag_days": lag}


TITLES = {
    "new_release": "📦 Обновление найдено! 🎉",
    "same_day_newer": "📦 Найден ещё один релиз с той же датой обновления 🎉",
    "earlier_date": "⏪ Дата обновления стала раньше (откат релиза или публикация задним числом)",
    "changed": "🔄 Изменились данные об обновлении",
}


def build_message(event):
    lines = [TITLES[event["kind"]],
             f"Было: {event['old']}",
             f"Стало: {event['new']}"]
    lag = event["lag_days"]
    if lag is not None:
        if lag <= 0:
            lines.append("Дата обновления - сегодня")
        else:
            lines.append(f"Дата обновления была {lag} дн. назад: публикация задним числом "
                         f"или поздно отобразилась в Google Play")
    lines.append(f"Ссылка для скачивания: {GOOGLE_PLAY_URL}")
    return "\n".join(lines)


# === Telegram ===
def tg(method, files=None, **params):
    resp = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/{method}",
                         data=params, files=files, timeout=20)
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram {method}: {data.get('description')}")
    return data["result"]


def get_group_description():
    return tg("getChat", chat_id=GROUP_CHAT_ID).get("description", "")


def update_group_description(text):
    tg("setChatDescription", chat_id=GROUP_CHAT_ID, description=text)


def send_notification(event):
    tg("sendMessage", chat_id=CHAT_ID, text=build_message(event), disable_web_page_preview="true")


# === Основной сценарий ===
def check_and_notify():
    log("Проверка обновлений...")
    obs, src = fetch_observation()
    if not obs:
        log("❌ Не удалось получить дату обновления.")
        return

    new_text = describe(obs)
    saved_text = clean(get_group_description())  # при ошибке исключение, ложных уведомлений не будет
    log(f"Новая дата на Google Play: {new_text} [{src}] | Старая дата на Google Play: {saved_text or 'нет'}")

    new, old = fields(new_text), fields(saved_text)
    if differs(new, old):
        log("🔔 Найдено обновление. Отправка уведомления...")
        send_notification(classify(new, old, now_local().date()))
        update_group_description(new_text)
    else:
        log("ℹ️ Обновлений нет.")
        # В описании старый формат (только дата), а теперь известны время и версия: дописываем молча
        if obs.get("ts") and new_text != saved_text:
            update_group_description(new_text)


if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Не задана переменная окружения BOT_TOKEN")
        sys.exit(2)
    try:
        check_and_notify()
    except Exception as e:
        log(f"❌ Ошибка: {safe(e)}")
        sys.exit(1)