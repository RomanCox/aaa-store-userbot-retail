import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from config import *
from utils.time_utils import is_working_hours
from services.channel_service import setup_channel_listener
from services.aaa_store_price_service import process_aaa_store_price
from services.apple_inside_channel_forwarder import setup_apple_inside_channel_forwarder, process_post
from services.today_here_tomorrow_there_price_service import process_today_here_tomorrow_there_price
from telethon.tl.functions.channels import JoinChannelRequest
import os
import time

HEARTBEAT_FILE = "/tmp/userbot_heartbeat"

async def heartbeat_loop():
    """Фоновая задача: каждые 2 минуты пишет timestamp в файл"""
    while True:
        try:
            with open(HEARTBEAT_FILE, 'w') as f:
                f.write(str(time.time()))
            # Можно добавить отладочный вывод, но не обязательно
            # print(f"❤️ Heartbeat записан в {HEARTBEAT_FILE}")
        except Exception as e:
            print(f"⚠️ Ошибка записи heartbeat: {e}")
        await asyncio.sleep(120)  # 2 минуты

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

async def poll_new_messages(client, source_channel, dest_channel, interval=30):
    try:
        last_msg = await client.get_messages(source_channel, limit=1)
        last_id = last_msg[0].id if last_msg else 0
        print(f"🔄 Последний известный ID: {last_id}")
    except Exception as e:
        print(f"⚠️ Не удалось получить последнее сообщение: {e}")
        last_id = 0

    print(f"🔄 Запущен опрос канала с интервалом {interval} сек.")
    while True:
        try:
            print(f"⏳ Опрос... (last_id={last_id})")
            # Получаем сообщения с ID > last_id
            messages = await client.get_messages(source_channel, limit=10, min_id=last_id)
            print(f"📨 Получено {len(messages)} сообщений с ID > {last_id}")
            if messages:
                # Сообщения приходят от новых к старым, перебираем в обратном порядке
                for msg in reversed(messages):
                    if msg.id > last_id:
                        print(f"📩 Найдено новое сообщение ID={msg.id}")
                        media_list = []
                        if msg.media and isinstance(msg.media, MessageMediaPhoto):
                            media_list.append(msg.media)
                        await process_post(client, msg.text or "", media_list, dest_channel, is_album=False)
                        last_id = msg.id
                    else:
                        print(f"   ⏭️ Пропускаем ID {msg.id} (старое)")
            else:
                print("   📭 Новых сообщений нет")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Ошибка при опросе: {e}")
        await asyncio.sleep(interval)

async def get_or_join_channel(client, channel_id, invite_link=None):
    try:
        entity = await client.get_entity(channel_id)
        print(f"✅ Канал найден: {entity.title} (ID: {entity.id})")
        return entity
    except ValueError:
        print(f"⚠️ Канал с ID {channel_id} не найден в диалогах.")
        if invite_link:
            print(f"🔗 Пытаемся вступить по ссылке: {invite_link}")
            try:
                entity = await client.get_entity(invite_link)
                # Вступаем через JoinChannelRequest
                await client(JoinChannelRequest(entity))
                print(f"✅ Успешно вступили в канал: {entity.title}")
                return entity
            except Exception as e:
                print(f"❌ Ошибка при вступлении по ссылке: {e}")
                raise
        else:
            print("❌ Нет ссылки для вступления. Пожалуйста, подпишитесь вручную.")
            raise

async def main():
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        await client.start(phone=PHONE)

        # 0. Запуск Heartbeat
        asyncio.create_task(heartbeat_loop())
        print("❤️ Heartbeat задача запущена")

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

        # 4. Запускаем слушатель для Apple-постов
        await client.get_dialogs()
        source_channel = await get_or_join_channel(
            client,
            NEWS_SOURCE_CHANNEL_ID,
            NEWS_SOURCE_CHANNEL_LINK
        )

        async for msg in client.iter_messages(source_channel, limit=1):
            print(f"📜 Последнее сообщение в канале: {msg.text[:100] if msg.text else '(медиа)'}")

        dest_channel = await get_or_join_channel(
            client,
            NEWS_DEST_CHANNEL_ID,
            NEWS_DEST_CHANNEL_LINK  # может быть None
        )

        await setup_apple_inside_channel_forwarder(client, source_channel, dest_channel)
        print("🍎 Слушаем канал для Apple-постов...")

        # asyncio.create_task(poll_new_messages(client, source_channel, dest_channel, interval=POLL_INTERVAL_SECONDS))
        # print("🔄 Запущен периодический опрос канала...")

        asyncio.create_task(periodic_price1())

        # Бесконечное ожидание (чтобы не завершиться)
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            print("🛑 Остановка задач...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")