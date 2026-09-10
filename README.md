# UserBot

Это Telegram userbot, написанный на Python с использованием Telethon.

---

## Быстрый запуск на сервере

### 1. Подключение к серверу
```bash
ssh h99447@vh154.hoster.by -p22
```

### 2. Перейти в директорию проекта
```bash
cd ~/bots/aaa-store-userbot-retail
```

### 3. Активировать виртуальное окружение
```bash
git fetch
git pull origin main
source venv/bin/activate
```

### 4. Установить зависимости (если нужно)
```bash
pip install -r requirements.txt
```

### 5. Запуск бота в фоне
```bash
nohup /var/www/h99447/data/bots/aaa-store-userbot-retail/venv/bin/python /var/www/h99447/data/bots/aaa-store-userbot-retail/main.py > bot.log 2>&1 &
```

### 6. Проверка работы бота
```bash
pgrep -af main.py
```

### Просмотр логов
```bash
tail -f bot.log
```

### Остановка бота
```bash
pkill -f main.py
```