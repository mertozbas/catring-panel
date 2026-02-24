from models.db import query_db, insert_db, update_db


def get_all_suppliers(active_only=True):
    if active_only:
        return query_db('SELECT * FROM suppliers WHERE is_active = 1 ORDER BY name')
    return query_db('SELECT * FROM suppliers ORDER BY name')


def get_supplier(supplier_id):
    return query_db('SELECT * FROM suppliers WHERE id = ?', [supplier_id], one=True)


def create_supplier(data):
    return insert_db(
        'INSERT INTO suppliers (name, contact_name, phone, address, category) VALUES (?, ?, ?, ?, ?)',
        [data.get('name'), data.get('contact_name'), data.get('phone'),
         data.get('address'), data.get('category')]
    )


def update_supplier(supplier_id, data):
    return update_db(
        'UPDATE suppliers SET name=?, contact_name=?, phone=?, address=?, category=? WHERE id=?',
        [data.get('name'), data.get('contact_name'), data.get('phone'),
         data.get('address'), data.get('category'), supplier_id]
    )


def toggle_supplier(supplier_id, active):
    return update_db('UPDATE suppliers SET is_active=? WHERE id=?', [active, supplier_id])
