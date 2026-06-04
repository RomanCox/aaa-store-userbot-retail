import asyncio
from config import MY_BOT

async def open_admin_panel(client):
    """
    Открывает админ-панель бота
    """
    my_bot = await client.get_entity(MY_BOT)

    await client.send_message(my_bot, "🫆 Панель админа")
    print("Открыли админку")

    await asyncio.sleep(3)

    return my_bot


async def click_upload_button(client, bot):
    """
    Нажимает кнопку '📤 Загрузить XLSX'
    """
    messages = await client.get_messages(bot, limit=5)

    for m in messages:
        if m.buttons:
            for row in m.buttons:
                for button in row:
                    if button.text == "📤 Загрузить XLSX":
                        await m.click(text="📤 Загрузить XLSX")
                        print("Кнопка загрузки нажата")
                        return True

    print("Кнопка не найдена")
    return False


async def send_price_file(client, bot, file_path):
    """
    Отправляет файл в бот
    """
    await asyncio.sleep(2)

    await client.send_file(bot, file_path, caption="Новый прайс")
    print("Файл отправлен")