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
    Отправляет файл в бота
    """
    await asyncio.sleep(2)
    await client.send_file(bot, file_path, caption="Новый прайс")
    print(f"📁 Файл отправлен: {file_path}")