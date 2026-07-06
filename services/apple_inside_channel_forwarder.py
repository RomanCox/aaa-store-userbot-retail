import os
import re
import tempfile
from telethon import events
from telethon.tl.types import MessageMediaPhoto

def edit_text(text):
    new_text = text.replace("@appleinside", "@mobiletime_by")
    new_text = re.sub(r'https?://t\.me/appleinside', 'https://t.me/mobiletime_by', new_text)
    new_text = new_text.replace("#appleinside", "").strip()
    new_text = re.sub(r'\n\s*\n', '\n\n', new_text)
    new_text = re.sub(r' +', ' ', new_text)
    return new_text

async def process_post(client, text, media_list, dest_channel, is_album=False):
    temp_files = []
    MAX_CAPTION_LENGTH = 1024  # лимит Telegram для подписи к медиа
    try:
        print(f"🔍 Обработка поста: текст длиной {len(text)} символов")
        print(f"📝 Текст: {text[:200]}...")

        # Условия отбора
        if "#apple" not in text:
            print("❌ Пропускаем: нет '#apple'")
            return
        if "Реклама" in text and "ИНН " in text:
            print("❌ Пропускаем: есть 'Реклама' и 'ИНН ' одновременно")
            return

        print("✅ Условия выполнены, начинаем обработку...")
        edited_text = edit_text(text)

        # Скачиваем все фото во временные файлы
        for media in media_list:
            if isinstance(media, MessageMediaPhoto):
                fd, path = tempfile.mkstemp(suffix='.jpg', prefix='apple_')
                os.close(fd)
                try:
                    await client.download_media(media, file=path)
                    temp_files.append(path)
                    print(f"📸 Скачано фото: {path}")
                except Exception as e:
                    print(f"❌ Ошибка скачивания медиа: {e}")
                    if os.path.exists(path):
                        os.remove(path)

        # Если нет ни файлов, ни текста – ничего не отправляем
        if not temp_files and not edited_text.strip():
            print("⚠️ Нет ни текста, ни картинок – пропускаем")
            return

        # Отправка в целевой канал
        if temp_files:
            # Если текст длиннее лимита – отправляем фото без подписи, а текст отдельно
            if len(edited_text) > MAX_CAPTION_LENGTH:
                print(f"📏 Текст слишком длинный ({len(edited_text)} символов), отправляем фото и текст отдельно")
                # Отправляем медиа без подписи
                if len(temp_files) > 1 or is_album:
                    await client.send_file(dest_channel, temp_files, caption='', parse_mode='html')
                else:
                    await client.send_file(dest_channel, temp_files[0], caption='', parse_mode='html')
                # Отправляем текст отдельным сообщением
                await client.send_message(dest_channel, edited_text, parse_mode='html')
                print(f"✅ Пост переслан (фото + текст отдельно)")
            else:
                # Отправляем с подписью
                if len(temp_files) > 1 or is_album:
                    await client.send_file(dest_channel, temp_files, caption=edited_text, parse_mode='html')
                else:
                    await client.send_file(dest_channel, temp_files[0], caption=edited_text, parse_mode='html')
                print(f"✅ Пост переслан (с подписью)")
        else:
            # Только текст
            await client.send_message(dest_channel, edited_text, parse_mode='html')
            print(f"✅ Пост переслан (только текст)")

    except Exception as e:
        print(f"❌ Ошибка обработки поста: {e}")
        import traceback
        traceback.print_exc()
    finally:
        for path in temp_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                print(f"⚠️ Не удалось удалить {path}: {e}")

async def setup_apple_inside_channel_forwarder(client, source_channel, dest_channel):
    """
    Регистрирует обработчики для исходного канала (события).
    """
    # Обработчик одиночных сообщений
    @client.on(events.NewMessage(chats=source_channel))
    async def single_message_handler(event):
        print("📩 Получено новое сообщение (одиночное)")
        if event.message.grouped_id is not None:
            print("⏭️ Это часть альбома – пропускаем (будет обработано альбомным обработчиком)")
            return
        text = event.message.text or ""
        media = event.message.media
        if not text and not media:
            print("⏭️ Пустое сообщение – игнорируем")
            return
        media_list = [media] if media and isinstance(media, MessageMediaPhoto) else []
        await process_post(client, text, media_list, dest_channel, is_album=False)

    # Обработчик альбомов
    @client.on(events.Album(chats=source_channel))
    async def album_handler(event):
        print("📸 Получен альбом (группа медиа)")
        first_msg = event.messages[0]
        text = first_msg.text or ""
        media_list = []
        for msg in event.messages:
            if msg.media and isinstance(msg.media, MessageMediaPhoto):
                media_list.append(msg.media)
        await process_post(client, text, media_list, dest_channel, is_album=True)