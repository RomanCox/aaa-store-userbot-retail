import asyncio
from telethon import TelegramClient

from config import *
from utils.time_utils import is_working_hours
from services.channel_service import setup_channel_listener
from services.process_service import process_once

async def main():
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        await client.start(phone=PHONE)

        # пример использования поиска канала
        channel = await client.get_entity(TODAY_THERE_TOMORROW_HERE_CHANNEL_ID)

        setup_channel_listener(client, channel.id, DOWNLOAD_DIR)
        print("👀 Слушаем канал...")

        await client.run_until_disconnected()

        # while True:
        #     print("\n=== Новый цикл ===")
        #
        #     if not is_working_hours():
        #         print("Вне рабочего времени")
        #         await asyncio.sleep(INTERVAL_SECONDS)
        #         continue
        #
        #     try:
        #         await process_once(client)
        #     except Exception as e:
        #         print("Ошибка:", e)
        #
        #     print(f"Ждём {INTERVAL_SECONDS} секунд...\n")
        #     await asyncio.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(main())