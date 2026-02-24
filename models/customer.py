from models.db import query_db, insert_db, update_db


def get_all_customers(active_only=True):
    if active_only:
        return query_db('SELECT * FROM customers WHERE is_active = 1 ORDER BY name')
    return query_db('SELECT * FROM customers ORDER BY name')


def get_customer(customer_id):
    return query_db('SELECT * FROM customers WHERE id = ?', [customer_id], one=True)


def create_customer(data):
    return insert_db(
        '''INSERT INTO customers (name, contact_name, phone, telegram_chat_id, address,
           latitude, longitude, default_variety_count, default_container_type,
           default_portion_count, special_notes, segment, unit_price)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        [data.get('name'), data.get('contact_name'), data.get('phone'),
         data.get('telegram_chat_id'), data.get('address'),
         data.get('latitude'), data.get('longitude'),
         data.get('default_variety_count', 4), data.get('default_container_type', 'sefer_tasi'),
         data.get('default_portion_count'), data.get('special_notes'),
         data.get('segment', 'normal'), data.get('unit_price')]
    )


def update_customer(customer_id, data):
    return update_db(
        '''UPDATE customers SET name=?, contact_name=?, phone=?, telegram_chat_id=?,
           address=?, latitude=?, longitude=?, default_variety_count=?,
           default_container_type=?, default_portion_count=?, special_notes=?,
           segment=?, unit_price=?
           WHERE id=?''',
        [data.get('name'), data.get('contact_name'), data.get('phone'),
         data.get('telegram_chat_id'), data.get('address'),
         data.get('latitude'), data.get('longitude'),
         data.get('default_variety_count', 4), data.get('default_container_type', 'sefer_tasi'),
         data.get('default_portion_count'), data.get('special_notes'),
         data.get('segment', 'normal'), data.get('unit_price'), customer_id]
    )


def toggle_customer(customer_id, active):
    return update_db('UPDATE customers SET is_active=? WHERE id=?', [active, customer_id])


def search_customers(term):
    return query_db(
        'SELECT * FROM customers WHERE name LIKE ? AND is_active = 1 ORDER BY name',
        ['%' + term + '%']
    )


def get_customer_order_stats(customer_id):
    """Müşteri sipariş istatistikleri."""
    return query_db(
        '''SELECT COUNT(*) as total_orders,
                  COALESCE(SUM(portion_count),0) as total_portions,
                  MIN(date) as first_order,
                  MAX(date) as last_order
           FROM orders WHERE customer_id = ?''',
        [customer_id], one=True
    )
