# UserBot

Это Telegram userbot, написанный на Python с использованием Telethon.

---

## Быстрый запуск на сервере

### 1. Подключение к серверу
```bash
ssh mobileti@93.125.99.154
```

### 2. Перейти в директорию проекта
```bash
cd ~/repositories/aaa-store-userbot-retail
```

### 3. Активировать виртуальное окружение
```bash
source /home/mobileti/virtualenv/repositories/aaa-store-userbot-retail/3.10/bin/activate
```

### 4. Установить зависимости (если нужно)
```bash
pip install -r requirements.txt
```

### 5. Запуск бота в фоне
```bash
nohup python main.py > bot.log 2>&1 &
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