from models.db import query_db, insert_db, update_db, get_db


def get_unread_count(role=None):
    """Okunmamış bildirim sayısı."""
    if role and role != 'admin':
        return query_db(
            '''SELECT COUNT(*) as count FROM notifications
               WHERE is_read = 0 AND (target_role IS NULL OR target_role = ?)''',
            [role], one=True
        )['count']
    return query_db(
        'SELECT COUNT(*) as count FROM notifications WHERE is_read = 0',
        one=True
    )['count']


def get_recent_notifications(limit=10, role=None):
    """Son bildirimleri getir."""
    if role and role != 'admin':
        return query_db(
            '''SELECT * FROM notifications
               WHERE target_role IS NULL OR target_role = ?
               ORDER BY created_at DESC LIMIT ?''',
            [role, limit]
        )
    return query_db(
        'SELECT * FROM notifications ORDER BY created_at DESC LIMIT ?',
        [limit]
    )


def create_notification(notif_type, title, message=None, link=None, target_role=None):
    """Bildirim oluştur."""
    return insert_db(
        '''INSERT INTO notifications (type, title, message, link, target_role)
           VALUES (?, ?, ?, ?, ?)''',
        [notif_type, title, message, link, target_role]
    )


def mark_as_read(notification_id):
    """Bildirimi okundu işaretle."""
    return update_db('UPDATE notifications SET is_read = 1 WHERE id = ?', [notification_id])


def mark_all_read(role=None):
    """Tüm bildirimleri okundu işaretle."""
    if role and role != 'admin':
        return update_db(
            '''UPDATE notifications SET is_read = 1
               WHERE is_read = 0 AND (target_role IS NULL OR target_role = ?)''',
            [role]
        )
    return update_db('UPDATE notifications SET is_read = 1 WHERE is_read = 0')


def check_and_create_notifications():
    """Otomatik bildirim kontrolü - periyodik çağrılır."""
    from models import inventory as inv_model
    from models import finance as finance_model
    from datetime import date

    created = 0

    # 1. Düşük stok uyarıları
    low_stock = query_db(
        '''SELECT ingredient_name, current_stock, min_stock_level, unit
           FROM inventory WHERE current_stock < min_stock_level AND min_stock_level > 0'''
    )
    for item in low_stock:
        # Aynı gün aynı malzeme için bildirim var mı kontrol et
        existing = query_db(
            '''SELECT id FROM notifications
               WHERE type = 'low_stock' AND title LIKE ? AND DATE(created_at) = ?''',
            [f"%{item['ingredient_name']}%", date.today().isoformat()], one=True
        )
        if not existing:
            create_notification(
                'low_stock',
                f"Dusuk Stok: {item['ingredient_name']}",
                f"Mevcut: {item['current_stock']:.1f} {item['unit']} / Min: {item['min_stock_level']:.1f} {item['unit']}",
                '/inventory/',
                'admin'
            )
            created += 1

    # 2. Ödenmemiş fatura uyarıları
    unpaid = finance_model.get_unpaid_invoices()
    if unpaid and len(unpaid) > 0:
        existing = query_db(
            '''SELECT id FROM notifications
               WHERE type = 'unpaid_invoice' AND DATE(created_at) = ?''',
            [date.today().isoformat()], one=True
        )
        if not existing:
            total = sum(float(inv['total_amount'] or 0) + float(inv['tax_amount'] or 0) for inv in unpaid)
            create_notification(
                'unpaid_invoice',
                f"{len(unpaid)} odenmemis fatura",
                f"Toplam: {total:.0f} TL",
                '/erp/?tab=invoices',
                'muhasebe'
            )
            created += 1

    return created


def get_notification_icon(notif_type):
    """Bildirim tipi için ikon."""
    icons = {
        'low_stock': '📦',
        'unpaid_invoice': '💰',
        'delivery_complete': '✅',
        'new_order': '🆕',
        'route_complete': '🚛',
        'info': 'ℹ️',
    }
    return icons.get(notif_type, '🔔')
