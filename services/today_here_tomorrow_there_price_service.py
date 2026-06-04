import os
from utils.file_utils import has_file_changed
from services.bot_service import open_admin_panel, click_button_by_text, send_price_file
from config import DOWNLOAD_DIR

APPLE_PREFIX = "Apple"

def get_today_here_tomorrow_there_price_standard_path():
    """Возвращает путь к текущему актуальному Apple-файлу (без new_)"""
    for f in os.listdir(DOWNLOAD_DIR):
        if f.startswith(APPLE_PREFIX) and not f.startswith("new_"):
            return os.path.join(DOWNLOAD_DIR, f)
    return None

async def process_today_here_tomorrow_there_price(client, new_file_path: str):
    """
    Универсальная обработка скачанного Apple-файла (с пометкой new_):
    сравнить с существующим, при изменении – отправить.
    """
    if not os.path.exists(new_file_path):
        return

    standard_path = get_today_here_tomorrow_there_price_standard_path()
    changed = True
    if standard_path and os.path.exists(standard_path):
        changed = has_file_changed(new_file_path, standard_path)

    if changed:
        print("🍎 Apple-файл изменился, загружаем в админ-бота")
        # Удаляем старый Apple-файл (без new_)
        if standard_path and os.path.exists(standard_path):
            os.remove(standard_path)
        # Переименовываем новый, убирая new_
        new_base = os.path.basename(new_file_path)
        final_name = new_base[4:] if new_base.startswith("new_") else new_base
        final_path = os.path.join(DOWNLOAD_DIR, final_name)
        os.rename(new_file_path, final_path)

        # Отправляем
        admin_bot = await open_admin_panel(client)
        if await click_button_by_text(client, admin_bot, "📤 Загрузить прайс сегодня там, завтра тут"):
            await send_price_file(client, admin_bot, final_path)
        else:
            print("❌ Не удалось нажать кнопку для Apple-прайса")
    else:
        print("🍎 Apple-файл не изменился, удаляем временный")
        os.remove(new_file_path)