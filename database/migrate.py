"""Apply schema migrations to existing database."""
import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), 'basak_yemek.db')

# werkzeug import için proje kökünü path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print("=" * 50)
    print("  Başak Yemek - Veritabanı Migrasyonu")
    print("=" * 50)

    # 1. Add default_route_id to customers if not exists
    try:
        c.execute("ALTER TABLE customers ADD COLUMN default_route_id INTEGER")
        print("✓ customers.default_route_id eklendi")
    except sqlite3.OperationalError:
        print("- customers.default_route_id zaten var")

    # 2. Create inventory_transactions table
    c.execute("""
    CREATE TABLE IF NOT EXISTS inventory_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inventory_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        quantity REAL NOT NULL,
        source TEXT,
        reference_id INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (inventory_id) REFERENCES inventory(id)
    )""")
    print("✓ inventory_transactions tablosu kontrol edildi")

    # 3. Fix purchase_items.is_accepted DEFAULT: 0 → NULL
    # SQLite'da column default değiştirmek için tabloyu yeniden oluştur
    c.execute("SELECT sql FROM sqlite_master WHERE name='purchase_items' AND type='table'")
    table_sql = c.fetchone()
    if table_sql and 'DEFAULT 0' in table_sql[0]:
        print("  purchase_items tablosu yeniden oluşturuluyor (DEFAULT 0 → NULL)...")
        c.execute("ALTER TABLE purchase_items RENAME TO purchase_items_old")
        c.execute("""
        CREATE TABLE purchase_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER NOT NULL,
            ingredient_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            unit_price REAL,
            total_price REAL,
            is_accepted INTEGER DEFAULT NULL,
            rejection_reason TEXT,
            FOREIGN KEY (purchase_id) REFERENCES purchases(id)
        )""")
        c.execute("""
        INSERT INTO purchase_items (id, purchase_id, ingredient_name, quantity, unit, unit_price, total_price, is_accepted, rejection_reason)
        SELECT id, purchase_id, ingredient_name, quantity, unit, unit_price, total_price,
               CASE WHEN is_accepted = 0 AND (rejection_reason IS NULL OR rejection_reason = '') THEN NULL ELSE is_accepted END,
               rejection_reason
        FROM purchase_items_old
        """)
        c.execute("DROP TABLE purchase_items_old")
        print("✓ purchase_items tablosu güncellendi (is_accepted DEFAULT NULL)")
    else:
        print("- purchase_items.is_accepted zaten doğru")

    # 4. Create users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'admin',
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    print("✓ users tablosu kontrol edildi")

    # 5. Seed default users
    from werkzeug.security import generate_password_hash

    users_to_seed = [
        ('admin', 'admin123', 'Sistem Yöneticisi', 'admin'),
        ('mutfak', 'mutfak123', 'Mutfak Ekibi', 'mutfak'),
        ('diyetisyen', 'diyet123', 'Diyetisyen Hanım', 'diyetisyen'),
        ('sofor1', 'sofor123', 'Koray Bey', 'sofor'),
        ('siparis', 'siparis123', 'Sipariş Sorumlusu', 'siparis'),
        ('planlama', 'plan123', 'Planlama Sorumlusu', 'planlama'),
        ('muhasebe', 'muhasebe123', 'Muhasebe', 'muhasebe'),
    ]

    added_users = 0
    for username, pwd, full_name, role in users_to_seed:
        try:
            c.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                [username, generate_password_hash(pwd), full_name, role]
            )
            added_users += 1
        except sqlite3.IntegrityError:
            pass  # Kullanıcı zaten var

    if added_users > 0:
        print(f"✓ {added_users} kullanıcı oluşturuldu")
    else:
        print("- Tüm kullanıcılar zaten var")

    # 6. Add optimized_distance_km and optimized_duration_min to routes
    try:
        c.execute("ALTER TABLE routes ADD COLUMN optimized_distance_km REAL")
        print("✓ routes.optimized_distance_km eklendi")
    except sqlite3.OperationalError:
        print("- routes.optimized_distance_km zaten var")

    try:
        c.execute("ALTER TABLE routes ADD COLUMN optimized_duration_min INTEGER")
        print("✓ routes.optimized_duration_min eklendi")
    except sqlite3.OperationalError:
        print("- routes.optimized_duration_min zaten var")

    conn.commit()

    # 7. Add driver_id to users table
    try:
        c.execute("ALTER TABLE users ADD COLUMN driver_id INTEGER")
        print("✓ users.driver_id eklendi")
    except sqlite3.OperationalError:
        print("- users.driver_id zaten var")

    # 8. Link existing sofor1 user to driver_id=1 (Koray Bey)
    c.execute("UPDATE users SET driver_id = 1 WHERE username = 'sofor1' AND driver_id IS NULL")
    if c.rowcount > 0:
        print("✓ sofor1 kullanıcısı driver_id=1 (Koray Bey) ile eşleştirildi")

    # 9. Create driver-specific user accounts for remaining drivers
    driver_users = [
        ('sofor2', 'sofor123', 'Fuat Bey', 'sofor', 2),
        ('sofor3', 'sofor123', 'Kadir Bey', 'sofor', 3),
        ('sofor4', 'sofor123', 'Gürkan Bey', 'sofor', 4),
    ]

    added_driver_users = 0
    for username, pwd, full_name, role, driver_id in driver_users:
        try:
            c.execute(
                "INSERT INTO users (username, password_hash, full_name, role, driver_id) VALUES (?, ?, ?, ?, ?)",
                [username, generate_password_hash(pwd), full_name, role, driver_id]
            )
            added_driver_users += 1
        except sqlite3.IntegrityError:
            pass  # Kullanıcı zaten var

    if added_driver_users > 0:
        print(f"✓ {added_driver_users} şoför kullanıcısı oluşturuldu")
    else:
        print("- Tüm şoför kullanıcıları zaten var")

    conn.commit()

    # 10. Toplu geocoding: adresi olan ama koordinati olmayan musteriler
    import config
    if config.GOOGLE_MAPS_API_KEY:
        from utils.maps import geocode_address
        import time

        customers = conn.execute(
            "SELECT id, name, address FROM customers WHERE address IS NOT NULL AND address != '' AND latitude IS NULL"
        ).fetchall()

        if customers:
            print(f"\n  {len(customers)} müşteri geocode ediliyor...")
            geocoded = 0
            failed = 0
            for cust in customers:
                lat, lng = geocode_address(cust[2] if isinstance(cust, tuple) else cust['address'])
                if lat and lng:
                    conn.execute(
                        "UPDATE customers SET latitude=?, longitude=? WHERE id=?",
                        [lat, lng, cust[0] if isinstance(cust, tuple) else cust['id']]
                    )
                    name = cust[1] if isinstance(cust, tuple) else cust['name']
                    print(f"  ✓ {name}: {lat}, {lng}")
                    geocoded += 1
                else:
                    name = cust[1] if isinstance(cust, tuple) else cust['name']
                    print(f"  ✗ {name}: geocode başarısız")
                    failed += 1
                time.sleep(0.5)  # API rate limit
            conn.commit()
            print(f"  → {geocoded} başarılı, {failed} başarısız")
        else:
            print("- Geocode edilecek müşteri yok (tümünün koordinatı var veya adresi yok)")
    else:
        print("- GOOGLE_MAPS_API_KEY ayarlanmamış, geocoding atlandı")

    conn.close()

    print("")
    print("✅ Migrasyon tamamlandı!")
    print("")
    print("Kullanıcılar:")
    print("  admin / admin123 (Yönetici - tüm erişim)")
    print("  mutfak / mutfak123 (Mutfak)")
    print("  diyetisyen / diyet123 (Diyetisyen)")
    print("  sofor1 / sofor123 (Şoför - Koray Bey)")
    print("  sofor2 / sofor123 (Şoför - Fuat Bey)")
    print("  sofor3 / sofor123 (Şoför - Kadir Bey)")
    print("  sofor4 / sofor123 (Şoför - Gürkan Bey)")
    print("  siparis / siparis123 (Sipariş)")
    print("  planlama / plan123 (Planlama)")
    print("  muhasebe / muhasebe123 (Muhasebe)")


if __name__ == "__main__":
    migrate()
