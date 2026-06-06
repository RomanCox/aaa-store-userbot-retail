import os
import asyncio
from datetime import datetime, timezone
from utils.file_utils import has_file_changed
from services.bot_service import open_admin_panel, click_button_by_text, send_price_file
from config import DOWNLOAD_DIR, STANDARD_FILE_NAME, NEW_FILE_NAME, PARTNER_BOT

MAX_FILE_AGE_SECONDS = 300

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
    # 2️⃣ Сравниваем с предыдущим файлом
    standard_path = os.path.join(DOWNLOAD_DIR, STANDARD_FILE_NAME)
    
    if has_file_changed(new_file_path, standard_path):
        print("🔄 Файл изменился или новый — заменяем старый")
        if os.path.exists(standard_path):
            os.remove(standard_path)
        os.rename(new_file_path, standard_path)
    else:
        print("✅ Файл не изменился — удаляем новый")
        os.remove(new_file_path)
        return

    # -----------------------------
    # 3️⃣ Отправляем файл в админ-бота
    admin_bot = await open_admin_panel(client)
    if await click_button_by_text(client, admin_bot, "📤 Загрузить aaa-store прайс"):
        await send_price_file(client, admin_bot, standard_path)
    else:
        print("❌ Не удалось нажать кнопку для aaa-store")