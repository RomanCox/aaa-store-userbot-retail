import os
import shutil
import asyncio
from datetime import datetime
from config import MY_BOT, UPLOADED_FILES_DIR

async def open_admin_panel(client):
    """
    Открывает админ-панель бота
    """
    my_bot = await client.get_entity(MY_BOT)
    await client.send_message(my_bot, "🫆 Панель админа")
    print("Открыли админку")
    await asyncio.sleep(3)
    return my_bot

async def click_button_by_text(client, bot, button_text: str) -> bool:
    """
    Находит и нажимает кнопку с заданным текстом.
    """
    messages = await client.get_messages(bot, limit=5)
    for msg in messages:
        if msg.buttons:
            for row in msg.buttons:
                for button in row:
                    if button.text == button_text:
                        await msg.click(text=button_text)
                        print(f"✅ Кнопка '{button_text}' нажата")
                        return True
    print(f"❌ Кнопка '{button_text}' не найдена")
    return False

async def send_price_file(client, bot, file_path: str):
    """
    Отправляет файл в бота, и сохраняет копию отправленного файла
    в отдельную папку (UPLOADED_FILES_DIR) с меткой даты/времени в имени.
    """
    await asyncio.sleep(2)
    await client.send_file(bot, file_path, caption="Новый прайс")
    print(f"📁 Файл отправлен: {file_path}")
    archive_uploaded_file(file_path)

def archive_uploaded_file(file_path: str):
    """
    Копирует загруженный файл в UPLOADED_FILES_DIR, добавляя к имени
    дату и время отправки, чтобы сохранить историю всех upload'ов.
    """
    try:
        os.makedirs(UPLOADED_FILES_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_name = os.path.basename(file_path)
        archived_name = f"{timestamp}_{base_name}"
        archived_path = os.path.join(UPLOADED_FILES_DIR, archived_name)
        shutil.copy2(file_path, archived_path)
        print(f"🗂 Копия загруженного файла сохранена: {archived_path}")
    except Exception as e:
        print(f"⚠️ Не удалось сохранить копию загруженного файла: {e}")