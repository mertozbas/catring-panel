#!/bin/bash
# Render start script: schema + migrate + gunicorn

DB_PATH="database/basak_yemek.db"

# Veritabanı yoksa schema ve seed'i yükle
if [ ! -f "$DB_PATH" ]; then
    echo ">>> Veritabanı oluşturuluyor..."
    mkdir -p database
    sqlite3 "$DB_PATH" < database/schema.sql
    sqlite3 "$DB_PATH" < database/seed.sql
    echo ">>> Schema ve seed yüklendi."
fi

# Migration çalıştır
echo ">>> Migration çalıştırılıyor..."
python database/migrate.py

# Gunicorn başlat
echo ">>> Gunicorn başlatılıyor..."
exec gunicorn "app:create_app()" --bind "0.0.0.0:$PORT"
