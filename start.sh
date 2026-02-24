#!/bin/bash
# Render start script: init_db + migrate + gunicorn

echo ">>> Veritabanı kontrol ediliyor..."
python init_db.py

echo ">>> Migration çalıştırılıyor..."
python database/migrate.py

echo ">>> Gunicorn başlatılıyor..."
exec gunicorn "app:create_app()" --bind "0.0.0.0:$PORT"
