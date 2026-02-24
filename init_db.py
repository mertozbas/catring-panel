"""Render başlatma: veritabanı yoksa veya boşsa schema + seed yükle, sonra migrate çalıştır."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'basak_yemek.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
SEED_PATH = os.path.join(os.path.dirname(__file__), 'database', 'seed.sql')


def needs_init():
    """Veritabanı yoksa veya customers tablosu yoksa True döner."""
    if not os.path.exists(DB_PATH):
        return True
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
        result = cur.fetchone()
        conn.close()
        return result is None
    except Exception:
        return True


def init():
    if needs_init():
        print(">>> Veritabanı oluşturuluyor...")
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        # Eski boş/bozuk db varsa sil
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

        conn = sqlite3.connect(DB_PATH)

        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
        print(">>> Schema yüklendi.")

        if os.path.exists(SEED_PATH):
            with open(SEED_PATH, 'r') as f:
                conn.executescript(f.read())
            print(">>> Seed data yüklendi.")

        conn.close()
    else:
        print(">>> Veritabanı zaten mevcut, schema atlanıyor.")


if __name__ == '__main__':
    init()
