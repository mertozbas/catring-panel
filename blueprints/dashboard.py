from flask import Blueprint, render_template
from models.db import query_db, get_db
from datetime import date, timedelta

bp = Blueprint('dashboard', __name__)


def get_todays_menu(date_str):
    """Bugünkü menü öğelerini getir."""
    from datetime import datetime as dt
    d = dt.strptime(date_str, '%Y-%m-%d')
    day_of_week = d.weekday()
    db = get_db()
    menu = db.execute(
        """SELECT wm.id FROM weekly_menus wm
           WHERE wm.week_start_date <= ? AND wm.status = 'published'
           ORDER BY wm.week_start_date DESC LIMIT 1""",
        [date_str]
    ).fetchone()
    if not menu:
        return []
    items = db.execute(
        """SELECT item_name, category FROM menu_items
           WHERE weekly_menu_id = ? AND day_of_week = ?
           ORDER BY item_order""",
        [menu['id'], day_of_week]
    ).fetchall()
    return [dict(i) for i in items]


@bp.route('/dashboard')
def index():
    today = date.today().isoformat()

    # Temel istatistikler
    total_customers = query_db('SELECT COUNT(*) as c FROM customers WHERE is_active=1', one=True)['c']
    total_drivers = query_db('SELECT COUNT(*) as c FROM drivers WHERE is_active=1', one=True)['c']

    daily = query_db(
        '''SELECT COUNT(*) as total_orders, COALESCE(SUM(portion_count),0) as total_portions
           FROM orders WHERE date=?''', [today], one=True)

    routes_today = query_db('SELECT COUNT(*) as c FROM routes WHERE date=?', [today], one=True)['c']

    # Teslimat durum dağılımı
    status_counts = query_db(
        '''SELECT status, COUNT(*) as c, COALESCE(SUM(portion_count),0) as portions
           FROM orders WHERE date=? GROUP BY status''', [today])
    status_map = {s['status']: {'count': s['c'], 'portions': s['portions']} for s in status_counts}

    # Rota tamamlanma durumu
    route_progress = query_db(
        '''SELECT r.id, r.route_name, r.status as route_status,
            (SELECT COUNT(*) FROM orders WHERE route_id=r.id AND status='delivered') as delivered,
            (SELECT COUNT(*) FROM orders WHERE route_id=r.id) as total
            FROM routes r WHERE r.date=? ORDER BY r.id''', [today])

    # Düşük stok uyarıları
    low_stock = query_db(
        '''SELECT COUNT(*) as c FROM inventory
           WHERE current_stock < min_stock_level AND min_stock_level > 0''', one=True)['c']
    low_stock_items = query_db(
        '''SELECT ingredient_name, current_stock, min_stock_level, unit
           FROM inventory
           WHERE current_stock < min_stock_level AND min_stock_level > 0
           ORDER BY (current_stock / min_stock_level) ASC LIMIT 5''')

    # Ödenmemiş faturalar
    unpaid = query_db(
        "SELECT COALESCE(SUM(total_amount),0) as total FROM invoices WHERE status != 'paid'",
        one=True)['total']

    # Haftalık porsiyon trendi (son 7 gün)
    week_ago = (date.today() - timedelta(days=6)).isoformat()
    weekly_trend = query_db(
        '''SELECT date, COALESCE(SUM(portion_count),0) as portions, COUNT(*) as orders
           FROM orders WHERE date >= ? GROUP BY date ORDER BY date''', [week_ago])

    # Kap tipi dağılımı (bugün)
    container_dist = query_db(
        '''SELECT container_type, COALESCE(SUM(portion_count),0) as portions
           FROM orders WHERE date=? GROUP BY container_type''', [today])

    # Bugünün menüsü
    todays_menu = get_todays_menu(today)

    # Son siparişler
    recent_orders = query_db(
        '''SELECT o.*, c.name as customer_name
           FROM orders o JOIN customers c ON o.customer_id = c.id
           WHERE o.date = ? ORDER BY o.created_at DESC LIMIT 10''', [today])

    return render_template('dashboard.html',
                           today=today,
                           total_customers=total_customers,
                           total_drivers=total_drivers,
                           daily=daily,
                           routes_today=routes_today,
                           recent_orders=recent_orders,
                           status_map=status_map,
                           route_progress=route_progress,
                           low_stock=low_stock,
                           low_stock_items=low_stock_items,
                           unpaid=unpaid,
                           weekly_trend=weekly_trend,
                           container_dist=container_dist,
                           todays_menu=todays_menu)
