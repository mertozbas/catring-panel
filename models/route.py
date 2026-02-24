from models.db import query_db, insert_db, update_db, get_db


def get_routes_by_date(date):
    return query_db(
        '''SELECT r.*, d.name as driver_name
           FROM routes r
           JOIN drivers d ON r.driver_id = d.id
           WHERE r.date = ?
           ORDER BY d.name, r.service_number''',
        [date]
    )


def get_route(route_id):
    return query_db(
        '''SELECT r.*, d.name as driver_name
           FROM routes r JOIN drivers d ON r.driver_id = d.id
           WHERE r.id = ?''',
        [route_id], one=True
    )


def create_route(data):
    return insert_db(
        '''INSERT INTO routes (date, driver_id, service_number, route_name, status)
           VALUES (?, ?, ?, ?, ?)''',
        [data.get('date'), data.get('driver_id'), data.get('service_number', 1),
         data.get('route_name'), data.get('status', 'planned')]
    )


def update_route(route_id, data):
    return update_db(
        '''UPDATE routes SET driver_id=?, service_number=?, route_name=?, status=?
           WHERE id=?''',
        [data.get('driver_id'), data.get('service_number', 1),
         data.get('route_name'), data.get('status', 'planned'), route_id]
    )


def delete_route(route_id):
    db = get_db()
    db.execute('UPDATE orders SET route_id = NULL, delivery_sequence = NULL WHERE route_id = ?', [route_id])
    db.execute('DELETE FROM routes WHERE id = ?', [route_id])
    db.commit()


def update_route_status(route_id, status):
    return update_db('UPDATE routes SET status=? WHERE id=?', [status, route_id])


def update_route_optimization(route_id, distance_km, duration_min):
    return update_db(
        'UPDATE routes SET optimized_distance_km=?, optimized_duration_min=? WHERE id=?',
        [distance_km, duration_min, route_id]
    )


def update_route_totals(route_id):
    db = get_db()
    totals = db.execute(
        '''SELECT
             SUM(CASE WHEN container_type='sefer_tasi' THEN portion_count ELSE 0 END) as sefer_tasi,
             SUM(CASE WHEN container_type='paket' THEN portion_count ELSE 0 END) as paket,
             SUM(CASE WHEN container_type='tepsi' THEN portion_count ELSE 0 END) as tepsi,
             SUM(CASE WHEN container_type='poset' THEN portion_count ELSE 0 END) as poset,
             SUM(CASE WHEN container_type='kuvet' THEN portion_count ELSE 0 END) as kuvet,
             SUM(portion_count) as total
           FROM orders WHERE route_id = ?''',
        [route_id]
    ).fetchone()
    db.execute(
        '''UPDATE routes SET total_sefer_tasi=?, total_paket=?, total_tepsi=?,
           total_poset=?, total_kuvet=?, total_portions=? WHERE id=?''',
        [totals['sefer_tasi'] or 0, totals['paket'] or 0, totals['tepsi'] or 0,
         totals['poset'] or 0, totals['kuvet'] or 0, totals['total'] or 0, route_id]
    )
    db.commit()


def get_driver_routes_today(driver_id, date):
    return query_db(
        '''SELECT r.*, d.name as driver_name
           FROM routes r JOIN drivers d ON r.driver_id = d.id
           WHERE r.driver_id = ? AND r.date = ?
           ORDER BY r.service_number''',
        [driver_id, date]
    )


def auto_create_routes(date_str):
    """Aktif şoförler için otomatik rota oluştur (yoksa)."""
    db = get_db()
    existing = db.execute(
        'SELECT driver_id FROM routes WHERE date = ?', [date_str]
    ).fetchall()
    existing_ids = {r['driver_id'] for r in existing}

    drivers = db.execute(
        'SELECT * FROM drivers WHERE is_active = 1'
    ).fetchall()

    created = 0
    for d in drivers:
        if d['id'] in existing_ids:
            continue
        db.execute(
            '''INSERT INTO routes (date, driver_id, service_number, route_name, status)
               VALUES (?, ?, 1, ?, 'planned')''',
            [date_str, d['id'], f"{d['name']} - 1. Servis"]
        )
        created += 1

    db.commit()
    return created
