import os
from telethon import events
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


async def get_recent_messages(client, channel, days=2):
    """
    Получает сообщения за последние N дней (по умолчанию: вчера + сегодня)
    """
    tz = ZoneInfo("Europe/Moscow")
    now = datetime.now(tz)

    # начало периода (вчера 00:00)
    start_date = (now - timedelta(days=days-1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    print(f"Ищем сообщения с {start_date}")

    messages = []

    async for message in client.iter_messages(channel):
        if not message.date:
            continue

        msg_date = message.date.astimezone(tz)

        if msg_date < start_date:
            break  # дальше уже старые сообщения

        messages.append(message)

    return messages


async def find_and_download_apple_xlsx(messages, download_dir):
    """
    Ищет и скачивает файл, название которого начинается с 'Apple'
    """
    for msg in messages:
        if not msg.document:
            continue

        file = msg.file
        name = file.name or ""

        if name.lower().startswith("apple") and name.endswith(".xlsx"):
            print(f"📄 Найден нужный файл: {name}")

            path = await msg.download_media(
                file=os.path.join(download_dir, name)
            )

            print(f"⬇️ Скачан: {path}")
            return path

    print("❌ Apple XLSX файл не найден")
    return None


def setup_channel_listener(client, channel_id, download_dir):
    @client.on(events.NewMessage(chats=channel_id))
    async def handler(event):
        msg = event.message

        if not msg.document:
            return

        file = msg.file
        name = (file.name or "").lower()

        # фильтр: Apple + xlsx
        if name.startswith("apple") and name.endswith(".xlsx"):
            print(f"📥 Новый прайс найден: {file.name}")

            path = await msg.download_media(
                file=os.path.join(download_dir, file.name)
            )

            print(f"⬇️ Скачан файл: {path}")

            # тут можешь сразу запускать пайплайн
            # await process_price_file(path)