import os
import asyncio
from datetime import datetime, timezone
from utils.file_utils import (
    has_file_changed,
    add_timestamp_to_filename,
    find_latest_versioned_file,
    cleanup_old_versioned_files,
)
from services.bot_service import open_admin_panel, click_button_by_text, send_price_file
from config import DOWNLOAD_DIR, STANDARD_FILE_NAME, NEW_FILE_NAME, PARTNER_BOT, PRICE_HISTORY_MAX_AGE_DAYS

MAX_FILE_AGE_SECONDS = 300
# Имя файла без расширения, по которому ищутся версии этого прайса в DOWNLOAD_DIR
PRICE_PREFIX = os.path.splitext(STANDARD_FILE_NAME)[0]

async def process_aaa_store_price(client):
    """Периодическая задача для поставщика 1 (aaa-store)"""
    
    # -----------------------------
    # 1️⃣ Запрашиваем свежий файл у партнёрского бота
    partner_bot = await client.get_entity(PARTNER_BOT)
    print("📊 Отправляем '📊 Цены' партнёрскому боту...")
    await client.send_message(partner_bot, "📊 Цены")

    await asyncio.sleep(3)
    messages = await client.get_messages(partner_bot, limit=1)
    if not messages:
        print("❌ Партнёрский бот не ответил")
        return

    msg = messages[0]
    print("Ответ партнёрского бота:", msg.text)

    if msg.buttons:
        await msg.click(text="📊 Скачать Excel")
        print("✅ Кнопка '📊 Скачать Excel' нажата!")
    else:
        print("❌ Кнопок нет")
        return

    # Ждём, пока бот сгенерирует и пришлёт файл
    await asyncio.sleep(3)

    # Ищем свежий файл (с датой не старше MAX_FILE_AGE_SECONDS)
    messages = await client.get_messages(partner_bot, limit=5)
    new_file_path = None
    file_message_date = None

    for m in messages:
        if m.document:
            file_message_date = m.date
            if file_message_date.tzinfo is None:
                # Если дата без часового пояса, считаем её UTC
                file_message_date = file_message_date.replace(tzinfo=timezone.utc)
            now_utc = datetime.now(timezone.utc)
            age = (now_utc - file_message_date).total_seconds()

            if age > MAX_FILE_AGE_SECONDS:
                print(f"⏰ Файл слишком старый (возраст {age:.0f} сек > {MAX_FILE_AGE_SECONDS} сек), пропускаем")
                continue

            # Скачиваем файл
            new_file_path = await m.download_media(file=os.path.join(DOWNLOAD_DIR, NEW_FILE_NAME))
            print(f"📥 Скачан свежий файл (возраст {age:.0f} сек): {new_file_path}")
            break

    if not new_file_path:
        print("❌ Свежий файл не найден (возможно, бот не отправил или файл старый)")
        return

    # -----------------------------
    # 2️⃣ Сравниваем с последней сохранённой версией прайса в DOWNLOAD_DIR
    latest_path = find_latest_versioned_file(DOWNLOAD_DIR, PRICE_PREFIX)

    if has_file_changed(new_file_path, latest_path):
        print("🔄 Файл изменился или новый — сохраняем новую версию с меткой даты/времени")
        versioned_name = add_timestamp_to_filename(STANDARD_FILE_NAME)
        versioned_path = os.path.join(DOWNLOAD_DIR, versioned_name)
        os.rename(new_file_path, versioned_path)
    else:
        print("✅ Файл не изменился — удаляем новый")
        os.remove(new_file_path)
        return

    # -----------------------------
    # 3️⃣ Отправляем файл в админ-бота
    admin_bot = await open_admin_panel(client)
    if await click_button_by_text(client, admin_bot, "📤 Загрузить aaa-store прайс"):
        await send_price_file(client, admin_bot, versioned_path)
    else:
        print("❌ Не удалось нажать кнопку для aaa-store")

    # -----------------------------
    # 4️⃣ Чистим версии прайса старше PRICE_HISTORY_MAX_AGE_DAYS суток
    cleanup_old_versioned_files(DOWNLOAD_DIR, PRICE_PREFIX, PRICE_HISTORY_MAX_AGE_DAYS)