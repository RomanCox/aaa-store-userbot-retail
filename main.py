import os
import asyncio
import hashlib
from telethon import TelegramClient
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE_NUMBER")

PARTNER_BOT = "ThreeAStoreBot"
MY_BOT = "ThreeAShop_bot"
SESSION_NAME = "userbot_session"
INTERVAL_SECONDS = 3 * 60

if not API_ID or not API_HASH or not PHONE:
    raise ValueError("Не найдены переменные .env")

API_ID = int(API_ID)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

NEW_FILE_NAME = "new_Все товары.xlsx"       # временный файл
STANDARD_FILE_NAME = "Все товары.xlsx"      # актуальный файл

def get_file_hash(path):
    """Возвращает SHA256 хэш файла"""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def is_working_hours():
    now = datetime.now(ZoneInfo("Europe/Moscow"))
    return 11 <= now.hour < 21

async def process_once(client):
    # -----------------------------
    # 1️⃣ Получаем файл от партнёрского бота
    partner_bot = await client.get_entity(PARTNER_BOT)
    print("Отправляем '📊 Цены'...")
    await client.send_message(partner_bot, "📊 Цены")

    await asyncio.sleep(3)
    messages = await client.get_messages(partner_bot, limit=1)
    if not messages:
        print("Бот не ответил")
        return

    msg = messages[0]
    print("Ответ партнёрского бота:", msg.text)

    if msg.buttons:
        await msg.click(text="📊 Скачать Excel")
        print("Кнопка '📊 Скачать Excel' нажата!")
    else:
        print("Кнопок нет")
        return

    await asyncio.sleep(3)  # ждём приход файла
    messages = await client.get_messages(partner_bot, limit=5)

    new_file_path = None
    for m in messages:
        if m.document:
            new_file_path = await m.download_media(file=os.path.join(DOWNLOAD_DIR, NEW_FILE_NAME))
            print("Файл скачан:", new_file_path)
            break
    else:
        print("Файл не найден")
        return

    # -----------------------------
    # 2️⃣ Сравниваем с предыдущим файлом
    standard_path = os.path.join(DOWNLOAD_DIR, STANDARD_FILE_NAME)
    new_file_path = os.path.join(DOWNLOAD_DIR, NEW_FILE_NAME)

    if os.path.exists(standard_path):
        if get_file_hash(standard_path) == get_file_hash(new_file_path):
            print("Файл не изменился — удаляем новый")
            os.remove(new_file_path)
            return
        else:
            print("Файл изменился — заменяем старый")
            os.remove(standard_path)
            os.rename(new_file_path, standard_path)
    else:
        os.rename(new_file_path, standard_path)
        print("Сохраняем новый файл как актуальный")

    # -----------------------------
    # 3️⃣ Отправляем файл в ваш бот
    my_bot = await client.get_entity(MY_BOT)
    await client.send_message(my_bot, "🫆 Панель админа")
    print("Сообщение '🫆 Панель админа' отправлено!")

    await asyncio.sleep(3)
    messages = await client.get_messages(my_bot, limit=5)
    upload_msg = None
    for m in messages:
        if m.buttons:
            for row in m.buttons:
                for button in row:
                    if button.text == "📤 Загрузить XLSX":
                        upload_msg = m
                        break
    if not upload_msg:
        print("Кнопка '📤 Загрузить XLSX' не найдена")
        return

    await upload_msg.click(text="📤 Загрузить XLSX")
    print("Кнопка '📤 Загрузить XLSX' нажата!")

    await asyncio.sleep(2)
    await client.send_file(my_bot, standard_path, caption="Новый прайс")
    print("Файл отправлен в ваш бот!")

async def main():
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        await client.start(phone=PHONE)

        while True:
            print("\n=== Новый цикл ===")

            if not is_working_hours():
                print("Сейчас вне рабочего времени (МСК). Спим...")
                await asyncio.sleep(INTERVAL_SECONDS)
                continue

            try:
                await process_once(client)
            except Exception as e:
                print("Ошибка в цикле:", e)

            print(f"Ждём {INTERVAL_SECONDS} секунд...\n")
            await asyncio.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(main())