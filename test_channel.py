import asyncio
from telethon import TelegramClient
from config import *
from services.today_here_tomorrow_there_price_service import process_today_here_tomorrow_there_price
import os

async def test():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    channel = await client.get_entity(TODAY_THERE_TOMORROW_HERE_CHANNEL_ID)
    async for msg in client.iter_messages(channel, limit=20):
        if msg.document:
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
                print(f"Скачан: {new_path}")
                await process_today_here_tomorrow_there_price(client, new_path)
                break
    await client.disconnect()

asyncio.run(test())