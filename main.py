import asyncio
from telethon import TelegramClient
from config import *
from utils.time_utils import is_working_hours
from services.channel_service import setup_channel_listener
from services.aaa_store_price_service import process_aaa_store_price
from services.today_here_tomorrow_there_price_service import process_today_here_tomorrow_there_price
import os

async def get_last_today_here_tomorrow_there_price_from_channel(client, channel_id):
    print("🔍 Ищем Apple-файл в канале...")
    channel = await client.get_entity(channel_id)
    async for msg in client.iter_messages(channel, limit=20):
        if msg.document:
            # Надёжное получение имени файла
            file_name = None
            if msg.file and msg.file.name:
                file_name = msg.file.name
            else:
                for attr in msg.document.attributes:
                    if hasattr(attr, 'file_name') and attr.file_name:
                        file_name = attr.file_name
                        break
            if file_name and file_name.startswith("Apple"):
                new_path = os.path.join(DOWNLOAD_DIR, f"new_{file_name}")
                await msg.download_media(file=new_path)
                print(f"📥 При старте скачан Apple-файл: {new_path}")
                await process_today_here_tomorrow_there_price(client, new_path)
                return
    print("❌ Apple-файл не найден в последних 20 сообщениях")

async def main():
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        await client.start(phone=PHONE)

        # 1. При старте – обработать последний Apple-файл из канала
        await get_last_today_here_tomorrow_there_price_from_channel(client, TODAY_THERE_TOMORROW_HERE_CHANNEL_ID)

        # 2. Запустить слушатель канала (для новых Apple-файлов)
        asyncio.create_task(setup_channel_listener(client, TODAY_THERE_TOMORROW_HERE_CHANNEL_ID, DOWNLOAD_DIR))
        print("👀 Слушаем канал...")

        # 3. Периодическая задача для поставщика 1 (aaa-store)
        async def periodic_price1():
            while True:
                if is_working_hours():
                    await process_aaa_store_price(client)
                else:
                    print("Вне рабочего времени, aaa-store не обрабатывается")
                await asyncio.sleep(INTERVAL_SECONDS)

        asyncio.create_task(periodic_price1())

        # Бесконечное ожидание (чтобы не завершиться)
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())