from models.db import query_db, insert_db, update_db
from werkzeug.security import generate_password_hash, check_password_hash


def get_user_by_username(username):
    return query_db(
        'SELECT * FROM users WHERE username = ? AND is_active = 1',
        [username], one=True
    )


def get_user_by_id(user_id):
    return query_db(
        'SELECT * FROM users WHERE id = ?',
        [user_id], one=True
    )


def verify_password(user, password):
    if not user:
        return False
    return check_password_hash(user['password_hash'], password)


def get_all_users():
    return query_db(
        'SELECT id, username, full_name, role, is_active, created_at FROM users ORDER BY username'
    )


def create_user(data):
    return insert_db(
        'INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)',
        [data['username'], generate_password_hash(data['password']),
         data['full_name'], data['role']]
    )


def update_user(user_id, data):
    if 'password' in data and data['password']:
        return update_db(
            'UPDATE users SET full_name=?, role=?, password_hash=? WHERE id=?',
            [data['full_name'], data['role'],
             generate_password_hash(data['password']), user_id]
        )
    return update_db(
        'UPDATE users SET full_name=?, role=? WHERE id=?',
        [data['full_name'], data['role'], user_id]
    )


def toggle_user(user_id, active):
    return update_db('UPDATE users SET is_active=? WHERE id=?', [active, user_id])


def get_driver_id_for_user(user_id):
    """Kullanıcının bağlı driver_id'sini döndür."""
    user = query_db('SELECT driver_id FROM users WHERE id = ?', [user_id], one=True)
    return user['driver_id'] if user and user['driver_id'] else None
