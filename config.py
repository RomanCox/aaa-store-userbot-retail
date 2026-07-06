import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE_NUMBER")
TODAY_THERE_TOMORROW_HERE_CHANNEL_ID = int(os.getenv("TODAY_THERE_TOMORROW_HERE_CHANNEL_ID"))
NEWS_SOURCE_CHANNEL_ID = int(os.getenv("NEWS_SOURCE_CHANNEL_ID"))
NEWS_DEST_CHANNEL_ID = int(os.getenv("NEWS_DEST_CHANNEL_ID"))
NEWS_SOURCE_CHANNEL_LINK = os.getenv("NEWS_SOURCE_CHANNEL_LINK")
NEWS_DEST_CHANNEL_LINK = os.getenv("NEWS_DEST_CHANNEL_LINK")

PARTNER_BOT = "ThreeAStoreBot"
MY_BOT = "ThreeAShop_bot"

SESSION_NAME = "userbot_session"
INTERVAL_SECONDS = 3 * 60

DOWNLOAD_DIR = "downloads"
NEW_FILE_NAME = "new_Все товары.xlsx"
STANDARD_FILE_NAME = "Все товары.xlsx"

# TODAY_THERE_TOMORROW_HERE_CHANNEL_ID = -1001850837833

POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", 30))