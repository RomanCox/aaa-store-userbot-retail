import os
from utils.file_utils import (
    has_file_changed,
    add_timestamp_to_filename,
    find_latest_versioned_file,
    cleanup_old_versioned_files,
)
from services.bot_service import open_admin_panel, click_button_by_text, send_price_file
from config import DOWNLOAD_DIR, PRICE_HISTORY_MAX_AGE_DAYS

APPLE_PREFIX = "Apple"

async def process_today_here_tomorrow_there_price(client, new_file_path: str):
    """
    Универсальная обработка скачанного Apple-файла (с пометкой new_):
    сравнить с последней сохранённой версией в DOWNLOAD_DIR, при изменении —
    сохранить новую версию с меткой даты/времени (старые версии не удаляются)
    и отправить в админ-бота, после чего удалить версии старше
    PRICE_HISTORY_MAX_AGE_DAYS суток.
    """
    if not os.path.exists(new_file_path):
        return

    latest_path = find_latest_versioned_file(DOWNLOAD_DIR, APPLE_PREFIX)
    changed = has_file_changed(new_file_path, latest_path)

    if changed:
        print("🍎 Apple-файл изменился, сохраняем новую версию с меткой даты/времени")
        new_base = os.path.basename(new_file_path)
        original_name = new_base[4:] if new_base.startswith("new_") else new_base
        versioned_name = add_timestamp_to_filename(original_name)
        versioned_path = os.path.join(DOWNLOAD_DIR, versioned_name)
        os.rename(new_file_path, versioned_path)

        # Отправляем
        admin_bot = await open_admin_panel(client)
        if await click_button_by_text(client, admin_bot, "📤 Загрузить прайс сегодня там, завтра тут"):
            await send_price_file(client, admin_bot, versioned_path)
        else:
            print("❌ Не удалось нажать кнопку для Apple-прайса")

        # Чистим версии прайса старше PRICE_HISTORY_MAX_AGE_DAYS суток
        cleanup_old_versioned_files(DOWNLOAD_DIR, APPLE_PREFIX, PRICE_HISTORY_MAX_AGE_DAYS)
    else:
        print("🍎 Apple-файл не изменился, удаляем временный")
        os.remove(new_file_path)
