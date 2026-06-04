import os
import asyncio

from config import (
    PARTNER_BOT,
    DOWNLOAD_DIR,
    NEW_FILE_NAME,
    STANDARD_FILE_NAME
)
from utils.file_utils import get_file_hash


async def request_price_file(client):
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

    if not msg.buttons:
        print("Кнопок нет")
        return None

    await msg.click(text="📊 Скачать Excel")
    print("Кнопка нажата!")

    await asyncio.sleep(3)

    messages = await client.get_messages(partner_bot, limit=5)

    for m in messages:
        if m.document:
            path = await m.download_media(
                file=os.path.join(DOWNLOAD_DIR, NEW_FILE_NAME)
            )
            print("Файл скачан:", path)
            return path

    print("Файл не найден")
    return None


def process_price_file():
    """
    Сравнивает новый файл со старым и обновляет при необходимости
    """
    standard_path = os.path.join(DOWNLOAD_DIR, STANDARD_FILE_NAME)
    new_path = os.path.join(DOWNLOAD_DIR, NEW_FILE_NAME)

    if not os.path.exists(new_path):
        print("Нового файла нет")
        return None

    if os.path.exists(standard_path):
        if get_file_hash(standard_path) == get_file_hash(new_path):
            print("Файл не изменился — удаляем новый")
            os.remove(new_path)
            return None
        else:
            print("Файл изменился — обновляем")
            os.remove(standard_path)
            os.rename(new_path, standard_path)
    else:
        print("Сохраняем новый файл")
        os.rename(new_path, standard_path)
    return standard_path