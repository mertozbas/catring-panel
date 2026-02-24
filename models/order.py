from models.db import query_db, insert_db, update_db, get_db


def get_orders_by_date(date):
    return query_db(
        '''SELECT o.*, c.name as customer_name, c.default_container_type, c.special_notes as customer_notes
           FROM orders o
           JOIN customers c ON o.customer_id = c.id
           WHERE o.date = ?
           ORDER BY o.route_id, o.delivery_sequence''',
        [date]
    )


def get_orders_by_route(route_id):
    return query_db(
        '''SELECT o.*, c.name as customer_name, c.address, c.latitude, c.longitude,
                  c.special_notes as customer_notes
           FROM orders o
           JOIN customers c ON o.customer_id = c.id
           WHERE o.route_id = ?
           ORDER BY o.delivery_sequence''',
        [route_id]
    )


def get_order(order_id):
    return query_db(
        '''SELECT o.*, c.name as customer_name
           FROM orders o JOIN customers c ON o.customer_id = c.id
           WHERE o.id = ?''',
        [order_id], one=True
    )


def create_order(data):
    return insert_db(
        '''INSERT INTO orders (date, customer_id, route_id, delivery_sequence,
           variety_count, portion_count, portion_detail, container_type,
           special_notes, extra_items, cutlery_needed, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        [data.get('date'), data.get('customer_id'), data.get('route_id'),
         data.get('delivery_sequence'), data.get('variety_count', 4),
         data.get('portion_count'), data.get('portion_detail'),
         data.get('container_type', 'sefer_tasi'), data.get('special_notes'),
         data.get('extra_items'), data.get('cutlery_needed', 0),
         data.get('status', 'pending')]
    )


def update_order(order_id, data):
    return update_db(
        '''UPDATE orders SET customer_id=?, route_id=?, delivery_sequence=?,
           variety_count=?, portion_count=?, portion_detail=?, container_type=?,
           special_notes=?, extra_items=?, cutlery_needed=?, status=?
           WHERE id=?''',
        [data.get('customer_id'), data.get('route_id'), data.get('delivery_sequence'),
         data.get('variety_count', 4), data.get('portion_count'),
         data.get('portion_detail'), data.get('container_type', 'sefer_tasi'),
         data.get('special_notes'), data.get('extra_items'),
         data.get('cutlery_needed', 0), data.get('status', 'pending'), order_id]
    )


def delete_order(order_id):
    return update_db('DELETE FROM orders WHERE id = ?', [order_id])


def get_daily_summary(date):
    return query_db(
        '''SELECT
             COUNT(*) as total_orders,
             SUM(portion_count) as total_portions,
             SUM(CASE WHEN container_type='sefer_tasi' THEN portion_count ELSE 0 END) as sefer_tasi,
             SUM(CASE WHEN container_type='paket' THEN portion_count ELSE 0 END) as paket,
             SUM(CASE WHEN container_type='kuvet' THEN portion_count ELSE 0 END) as kuvet,
             SUM(CASE WHEN container_type='tepsi' THEN portion_count ELSE 0 END) as tepsi,
             SUM(CASE WHEN container_type='poset' THEN portion_count ELSE 0 END) as poset
           FROM orders WHERE date = ?''',
        [date], one=True
    )


def get_unassigned_orders(date):
    return query_db(
        '''SELECT o.*, c.name as customer_name
           FROM orders o JOIN customers c ON o.customer_id = c.id
           WHERE o.date = ? AND o.route_id IS NULL
           ORDER BY c.name''',
        [date]
    )


def assign_order_to_route(order_id, route_id, sequence):
    return update_db(
        'UPDATE orders SET route_id=?, delivery_sequence=? WHERE id=?',
        [route_id, sequence, order_id]
    )


def update_order_status(order_id, status):
    return update_db('UPDATE orders SET status=? WHERE id=?', [status, order_id])


def update_delivery_sequence(order_id, sequence):
    return update_db('UPDATE orders SET delivery_sequence=? WHERE id=?', [sequence, order_id])


def generate_daily_orders(date_str):
    """Aktif müşteriler için günlük siparişleri toplu oluştur."""
    db = get_db()
    # Bugün için zaten siparişi olan müşterileri bul
    existing = db.execute(
        'SELECT customer_id FROM orders WHERE date = ?', [date_str]
    ).fetchall()
    existing_ids = {r['customer_id'] for r in existing}

    # Aktif müşterileri al (porsiyon sayısı olanlar)
    customers = db.execute(
        'SELECT * FROM customers WHERE is_active = 1 AND default_portion_count IS NOT NULL AND default_portion_count > 0'
    ).fetchall()

    created = 0
    for c in customers:
        if c['id'] in existing_ids:
            continue
        db.execute(
            '''INSERT INTO orders (date, customer_id, variety_count, portion_count,
               container_type, special_notes, status)
               VALUES (?, ?, ?, ?, ?, ?, 'pending')''',
            [date_str, c['id'], c['default_variety_count'] or 4,
             c['default_portion_count'], c['default_container_type'] or 'sefer_tasi',
             c['special_notes']]
        )
        created += 1

    db.commit()
    return created


def auto_assign_routes(date_str):
    """Siparişleri müşterilerin varsayılan rotalarına otomatik ata."""
    db = get_db()
    # Rotası atanmamış siparişleri al
    unassigned = db.execute(
        '''SELECT o.id, o.customer_id, c.default_route_id
           FROM orders o
           JOIN customers c ON o.customer_id = c.id
           WHERE o.date = ? AND o.route_id IS NULL AND c.default_route_id IS NOT NULL''',
        [date_str]
    ).fetchall()

    assigned = 0
    route_sequences = {}  # route_id -> next sequence number

    for order in unassigned:
        route_id = order['default_route_id']
        # Rotanın bugünkü tarihte var olup olmadığını kontrol et
        route = db.execute(
            'SELECT id FROM routes WHERE id = ? AND date = ?',
            [route_id, date_str]
        ).fetchone()

        if route:
            if route_id not in route_sequences:
                max_seq = db.execute(
                    'SELECT MAX(delivery_sequence) as ms FROM orders WHERE route_id = ?',
                    [route_id]
                ).fetchone()
                route_sequences[route_id] = (max_seq['ms'] or 0) + 1

            seq = route_sequences[route_id]
            route_sequences[route_id] = seq + 1

            db.execute(
                'UPDATE orders SET route_id = ?, delivery_sequence = ? WHERE id = ?',
                [route_id, seq, order['id']]
            )
            assigned += 1

    db.commit()
    return assigned


def bulk_update_status(date_str, from_status, to_status):
    """Belirli tarihteki siparişlerin durumunu toplu güncelle."""
    db = get_db()
    result = db.execute(
        'UPDATE orders SET status = ? WHERE date = ? AND status = ?',
        [to_status, date_str, from_status]
    )
    db.commit()
    return result.rowcount


def get_orders_by_status(date_str, status):
    """Belirli durumdaki siparişleri getir."""
    return query_db(
        '''SELECT o.*, c.name as customer_name
           FROM orders o JOIN customers c ON o.customer_id = c.id
           WHERE o.date = ? AND o.status = ?
           ORDER BY o.route_id, o.delivery_sequence''',
        [date_str, status]
    )
