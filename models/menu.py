from models.db import query_db, insert_db, update_db, get_db


def get_all_menus():
    return query_db('SELECT * FROM weekly_menus ORDER BY week_start_date DESC')


def get_menu(menu_id):
    return query_db('SELECT * FROM weekly_menus WHERE id = ?', [menu_id], one=True)


def get_menu_by_week(week_start_date):
    return query_db('SELECT * FROM weekly_menus WHERE week_start_date = ?',
                     [week_start_date], one=True)


def get_current_week_menu():
    return query_db(
        '''SELECT * FROM weekly_menus
           WHERE week_start_date <= date('now')
           ORDER BY week_start_date DESC LIMIT 1''', one=True)


def create_menu(week_start_date):
    return insert_db(
        'INSERT INTO weekly_menus (week_start_date) VALUES (?)',
        [week_start_date]
    )


def update_menu_status(menu_id, status):
    return update_db('UPDATE weekly_menus SET status=? WHERE id=?', [status, menu_id])


def get_menu_items(menu_id):
    return query_db(
        'SELECT * FROM menu_items WHERE weekly_menu_id = ? ORDER BY day_of_week, item_order',
        [menu_id]
    )


def save_menu_items(menu_id, items):
    db = get_db()
    db.execute('DELETE FROM menu_items WHERE weekly_menu_id = ?', [menu_id])
    for item in items:
        db.execute(
            '''INSERT INTO menu_items (weekly_menu_id, day_of_week, item_order, item_name, category)
               VALUES (?, ?, ?, ?, ?)''',
            [menu_id, item['day_of_week'], item['item_order'],
             item['item_name'], item.get('category')]
        )
    db.commit()


def delete_menu(menu_id):
    db = get_db()
    db.execute('DELETE FROM menu_items WHERE weekly_menu_id = ?', [menu_id])
    db.execute('DELETE FROM weekly_menus WHERE id = ?', [menu_id])
    db.commit()
