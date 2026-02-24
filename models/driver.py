from models.db import query_db, insert_db, update_db


def get_all_drivers(active_only=True):
    if active_only:
        return query_db('SELECT * FROM drivers WHERE is_active = 1 ORDER BY name')
    return query_db('SELECT * FROM drivers ORDER BY name')


def get_driver(driver_id):
    return query_db('SELECT * FROM drivers WHERE id = ?', [driver_id], one=True)


def create_driver(data):
    return insert_db(
        'INSERT INTO drivers (name, phone, telegram_chat_id) VALUES (?, ?, ?)',
        [data.get('name'), data.get('phone'), data.get('telegram_chat_id')]
    )


def update_driver(driver_id, data):
    return update_db(
        'UPDATE drivers SET name=?, phone=?, telegram_chat_id=? WHERE id=?',
        [data.get('name'), data.get('phone'), data.get('telegram_chat_id'), driver_id]
    )


def toggle_driver(driver_id, active):
    return update_db('UPDATE drivers SET is_active=? WHERE id=?', [active, driver_id])
