#!/bin/bash
# Render start script: init_db + migrate + gunicorn + telegram bot

echo ">>> Veritabanı kontrol ediliyor..."
python init_db.py

echo ">>> Migration çalıştırılıyor..."
python database/migrate.py

# Telegram bot'u background'da başlat (TELEGRAM_BOT_TOKEN varsa)
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    echo ">>> Telegram bot başlatılıyor (background)..."
    python agent/bot.py &
    BOT_PID=$!
    echo ">>> Telegram bot PID: $BOT_PID"
else
    echo ">>> TELEGRAM_BOT_TOKEN yok, bot atlanıyor."
fi

echo ">>> Gunicorn başlatılıyor..."
exec gunicorn "app:create_app()" --bind "0.0.0.0:$PORT"
