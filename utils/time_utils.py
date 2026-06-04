from datetime import datetime
from zoneinfo import ZoneInfo

def is_working_hours():
    now = datetime.now(ZoneInfo("Europe/Moscow"))
    return 11 <= now.hour < 21