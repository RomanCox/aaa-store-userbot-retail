import os
import asyncio
from telethon import events
from config import DOWNLOAD_DIR
from services.today_here_tomorrow_there_price_service import process_today_here_tomorrow_there_price

async def setup_channel_listener(client, channel_id, download_dir):
    """
    Регистрирует обработчик новых сообщений в канале.
    При появлении файла с именем, начинающимся на "Apple", скачивает как new_* и обрабатывает.
    """
    @client.on(events.NewMessage(chats=channel_id))
    async def handler(event):
        if event.message.document:
            file_name = event.message.file.name
            if file_name and file_name.startswith("Apple"):
                # Скачиваем с префиксом new_
                new_file_path = os.path.join(download_dir, f"new_{file_name}")
                await event.message.download_media(file=new_file_path)
                print(f"📥 Скачан новый Apple-файл: {new_file_path}")
                await process_today_here_tomorrow_there_price(client, new_file_path)

    # Бесконечно держим слушателя (но не блокируем остальной код)
    await asyncio.Event().wait()  # вечное ожидание