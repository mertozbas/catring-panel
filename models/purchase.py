from models.db import query_db, insert_db, update_db, get_db


def get_all_purchases():
    return query_db(
        '''SELECT p.*, s.name as supplier_name
           FROM purchases p JOIN suppliers s ON p.supplier_id = s.id
           ORDER BY p.date DESC'''
    )


def get_purchase(purchase_id):
    return query_db(
        '''SELECT p.*, s.name as supplier_name
           FROM purchases p JOIN suppliers s ON p.supplier_id = s.id
           WHERE p.id = ?''',
        [purchase_id], one=True
    )


def create_purchase(data):
    return insert_db(
        'INSERT INTO purchases (supplier_id, date, total_amount, status) VALUES (?, ?, ?, ?)',
        [data.get('supplier_id'), data.get('date'),
         data.get('total_amount', 0), data.get('status', 'pending')]
    )


def update_purchase_status(purchase_id, status):
    return update_db('UPDATE purchases SET status=? WHERE id=?', [status, purchase_id])


def get_purchase_items(purchase_id):
    return query_db('SELECT * FROM purchase_items WHERE purchase_id = ? ORDER BY ingredient_name', [purchase_id])


def add_purchase_item(data):
    return insert_db(
        '''INSERT INTO purchase_items (purchase_id, ingredient_name, quantity, unit, unit_price, total_price)
           VALUES (?, ?, ?, ?, ?, ?)''',
        [data.get('purchase_id'), data.get('ingredient_name'), data.get('quantity'),
         data.get('unit'), data.get('unit_price'), data.get('total_price')]
    )


def save_purchase_items(purchase_id, items):
    db = get_db()
    db.execute('DELETE FROM purchase_items WHERE purchase_id = ?', [purchase_id])
    total = 0
    for item in items:
        tp = float(item.get('quantity', 0)) * float(item.get('unit_price', 0))
        db.execute(
            '''INSERT INTO purchase_items (purchase_id, ingredient_name, quantity, unit, unit_price, total_price)
               VALUES (?, ?, ?, ?, ?, ?)''',
            [purchase_id, item['ingredient_name'], item['quantity'],
             item['unit'], item.get('unit_price', 0), tp]
        )
        total += tp
    db.execute('UPDATE purchases SET total_amount=? WHERE id=?', [total, purchase_id])
    db.commit()


def inspect_purchase_item(item_id, accepted, reason=None):
    return update_db(
        'UPDATE purchase_items SET is_accepted=?, rejection_reason=? WHERE id=?',
        [1 if accepted else 0, reason, item_id]
    )


def inspect_purchase(purchase_id, inspected_by, notes):
    return update_db(
        'UPDATE purchases SET status=?, inspected_by=?, inspection_notes=? WHERE id=?',
        ['inspected', inspected_by, notes, purchase_id]
    )
