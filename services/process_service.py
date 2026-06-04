from services.price_service import request_price_file, process_price_file
from services.bot_service import (
    open_admin_panel,
    click_upload_button,
    send_price_file
)


async def process_once(client):
    # 1. Скачать файл
    new_file = await request_price_file(client)
    if not new_file:
        return

    # 2. Обработать (сравнить)
    final_file = process_price_file()
    if not final_file:
        return

    # 3. Отправить в бот
    bot = await open_admin_panel(client)

    success = await click_upload_button(client, bot)
    if not success:
        return

    await send_price_file(client, bot, final_file)