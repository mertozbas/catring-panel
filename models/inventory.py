from models.db import query_db, insert_db, update_db, get_db


def get_all_inventory():
    return query_db('SELECT * FROM inventory ORDER BY ingredient_name')


def get_inventory_item(item_id):
    return query_db('SELECT * FROM inventory WHERE id = ?', [item_id], one=True)


def get_inventory_by_name(name):
    return query_db('SELECT * FROM inventory WHERE ingredient_name = ?', [name], one=True)


def create_inventory_item(data):
    return insert_db(
        'INSERT INTO inventory (ingredient_name, current_stock, unit, min_stock_level) VALUES (?, ?, ?, ?)',
        [data.get('ingredient_name'), data.get('current_stock', 0),
         data.get('unit'), data.get('min_stock_level', 0)]
    )


def update_inventory_item(item_id, data):
    return update_db(
        'UPDATE inventory SET ingredient_name=?, current_stock=?, unit=?, min_stock_level=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
        [data.get('ingredient_name'), data.get('current_stock', 0),
         data.get('unit'), data.get('min_stock_level', 0), item_id]
    )


def update_stock(item_id, quantity_change):
    return update_db(
        'UPDATE inventory SET current_stock = current_stock + ?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
        [quantity_change, item_id]
    )


def add_stock(item_id, quantity, source='manual', reference_id=None, notes=None):
    """Stok ekle ve hareket kaydı oluştur."""
    db = get_db()
    db.execute(
        'UPDATE inventory SET current_stock = current_stock + ?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
        [quantity, item_id]
    )
    db.execute(
        '''INSERT INTO inventory_transactions (inventory_id, type, quantity, source, reference_id, notes)
           VALUES (?, 'in', ?, ?, ?, ?)''',
        [item_id, quantity, source, reference_id, notes]
    )
    db.commit()


def deduct_stock(item_id, quantity, source='production', reference_id=None, notes=None):
    """Stok düş ve hareket kaydı oluştur."""
    db = get_db()
    db.execute(
        'UPDATE inventory SET current_stock = current_stock - ?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
        [quantity, item_id]
    )
    db.execute(
        '''INSERT INTO inventory_transactions (inventory_id, type, quantity, source, reference_id, notes)
           VALUES (?, 'out', ?, ?, ?, ?)''',
        [item_id, quantity, source, reference_id, notes]
    )
    db.commit()


def add_stock_from_purchase(purchase_id):
    """Satınalma onayından sonra kabul edilen kalemleri stoka ekle."""
    db = get_db()
    items = db.execute(
        'SELECT * FROM purchase_items WHERE purchase_id = ? AND is_accepted = 1',
        [purchase_id]
    ).fetchall()

    added = 0
    for item in items:
        # Envanterde bu malzeme var mı?
        inv = db.execute(
            'SELECT id FROM inventory WHERE ingredient_name = ?',
            [item['ingredient_name']]
        ).fetchone()

        if inv:
            inv_id = inv['id']
        else:
            # Yoksa oluştur
            cursor = db.execute(
                'INSERT INTO inventory (ingredient_name, current_stock, unit, min_stock_level) VALUES (?, 0, ?, 0)',
                [item['ingredient_name'], item['unit']]
            )
            inv_id = cursor.lastrowid

        # Stoku artır
        db.execute(
            'UPDATE inventory SET current_stock = current_stock + ?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
            [item['quantity'], inv_id]
        )
        # Hareket kaydı
        db.execute(
            '''INSERT INTO inventory_transactions (inventory_id, type, quantity, source, reference_id, notes)
               VALUES (?, 'in', ?, 'purchase', ?, ?)''',
            [inv_id, item['quantity'], purchase_id, f"Satınalma #{purchase_id}"]
        )
        added += 1

    db.commit()
    return added


def deduct_stock_for_production(date_str, total_portions):
    """Üretim için stoktan malzeme düş (tarife göre)."""
    from models import recipe as recipe_model
    from models import menu as menu_model
    from datetime import date as dt

    db = get_db()
    current_menu = menu_model.get_current_week_menu()
    if not current_menu:
        return 0

    day_of_week = dt.fromisoformat(date_str).weekday()
    if day_of_week >= 6:
        return 0

    menu_items = db.execute(
        'SELECT * FROM menu_items WHERE weekly_menu_id=? AND day_of_week=?',
        [current_menu['id'], day_of_week]
    ).fetchall()

    deducted = 0
    for mi in menu_items:
        recipe = recipe_model.get_recipe_by_name(mi['item_name'])
        if not recipe:
            continue
        ingredients = recipe_model.get_recipe_ingredients(recipe['id'])
        for ing in ingredients:
            needed = ing['quantity_per_person'] * total_portions
            inv = db.execute(
                'SELECT id FROM inventory WHERE ingredient_name = ?',
                [ing['ingredient_name']]
            ).fetchone()
            if inv:
                db.execute(
                    'UPDATE inventory SET current_stock = MAX(0, current_stock - ?), updated_at=CURRENT_TIMESTAMP WHERE id=?',
                    [needed, inv['id']]
                )
                db.execute(
                    '''INSERT INTO inventory_transactions (inventory_id, type, quantity, source, reference_id, notes)
                       VALUES (?, 'out', ?, 'production', NULL, ?)''',
                    [inv['id'], needed, f"Üretim {date_str} - {mi['item_name']}"]
                )
                deducted += 1

    db.commit()
    return deducted


def get_stock_transactions(item_id=None, limit=50):
    """Stok hareket geçmişi."""
    if item_id:
        return query_db(
            '''SELECT it.*, i.ingredient_name, i.unit
               FROM inventory_transactions it
               JOIN inventory i ON it.inventory_id = i.id
               WHERE it.inventory_id = ?
               ORDER BY it.created_at DESC LIMIT ?''',
            [item_id, limit]
        )
    return query_db(
        '''SELECT it.*, i.ingredient_name, i.unit
           FROM inventory_transactions it
           JOIN inventory i ON it.inventory_id = i.id
           ORDER BY it.created_at DESC LIMIT ?''',
        [limit]
    )


def get_low_stock_items():
    return query_db('SELECT * FROM inventory WHERE current_stock <= min_stock_level ORDER BY ingredient_name')


def delete_inventory_item(item_id):
    return update_db('DELETE FROM inventory WHERE id = ?', [item_id])
