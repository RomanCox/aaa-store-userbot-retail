import os
from typing import Optional
from utils.file_utils import has_file_changed
from services.bot_service import open_admin_panel, click_button_by_text, send_price_file
from config import DOWNLOAD_DIR, STANDARD_FILE_NAME, NEW_FILE_NAME, PARTNER_BOT

async def download_aaa_store_price_from_source(client) -> Optional[str]:
    """
    Скачивает файл из бота-источника (ThreeAStoreBot) в DOWNLOAD_DIR с именем NEW_FILE_NAME.
    Возвращает путь к скачанному файлу или None.
    """
    partner_bot = await client.get_entity(PARTNER_BOT)
    # Ищем последнее сообщение с файлом
    messages = await client.get_messages(partner_bot, limit=5)
    for msg in messages:
        if msg.document:
            # Скачиваем с именем NEW_FILE_NAME
            file_path = await msg.download_media(file=os.path.join(DOWNLOAD_DIR, NEW_FILE_NAME))
            return file_path
    return None

async def process_aaa_store_price(client):
    """Периодическая задача для поставщика 1"""
    new_file = await download_aaa_store_price_from_source(client)
    if not new_file:
        print("❌ Не удалось скачать новый прайс от поставщика 1")
        return

    standard_path = os.path.join(DOWNLOAD_DIR, STANDARD_FILE_NAME)
    changed = has_file_changed(new_file, standard_path)

    if changed:
        print("🔄 Файл aaa-store изменился, загружаем в админ-бота")
        # Удаляем старый, если есть
        if os.path.exists(standard_path):
            os.remove(standard_path)
        # Переименовываем новый (убираем new_)
        os.rename(new_file, standard_path)

        # Отправляем в админ-бота
        admin_bot = await open_admin_panel(client)
        if await click_button_by_text(client, admin_bot, "📤 Загрузить aaa-store прайс"):
            await send_price_file(client, admin_bot, standard_path)
        else:
            print("❌ Не удалось нажать кнопку для aaa-store")
    else:
        print("✅ Файл aaa-store не изменился, удаляем временный")
        os.remove(new_file)