from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import route as route_model
from models import order as order_model
from models import driver as driver_model
from models.db import insert_db, get_db
from datetime import date, datetime
import config

bp = Blueprint('driver_ui', __name__)


def get_todays_menu(date_str):
    """Bugünkü menü öğelerini getir."""
    db = get_db()
    from datetime import datetime as dt
    d = dt.strptime(date_str, '%Y-%m-%d')
    day_of_week = d.weekday()  # 0=Pazartesi, 6=Pazar

    # En güncel yayınlanmış haftalık menüyü bul
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


@bp.route('/')
def index():
    driver_id = session.get('driver_id')
    if not driver_id:
        flash('Şoför hesabınız bir şoföre bağlanmamış. Yöneticiye başvurun.', 'danger')
        return redirect(url_for('auth.login'))

    today = date.today().isoformat()
    driver = driver_model.get_driver(driver_id)
    routes = route_model.get_driver_routes_today(driver_id, today)

    route_orders = {}
    for r in routes:
        route_orders[r['id']] = order_model.get_orders_by_route(r['id'])

    today_menu = get_todays_menu(today)

    return render_template('driver.html',
                           driver_id=driver_id,
                           driver_name=driver['name'] if driver else 'Şoför',
                           routes=routes,
                           route_orders=route_orders,
                           today=today,
                           today_menu=today_menu,
                           google_maps_key=config.GOOGLE_MAPS_API_KEY)


@bp.route('/deliver/<int:order_id>', methods=['POST'])
def deliver(order_id):
    driver_id = session.get('driver_id')
    order_model.update_order_status(order_id, 'delivered')
    order = order_model.get_order(order_id)
    if order:
        insert_db(
            '''INSERT INTO delivery_confirmations (order_id, route_id, driver_id, delivered_at, notes)
               VALUES (?, ?, ?, ?, ?)''',
            [order_id, order['route_id'], driver_id,
             datetime.now().isoformat(), request.form.get('notes', '')]
        )
    flash('Teslimat onaylandı.', 'success')
    return redirect(url_for('driver_ui.index'))


@bp.route('/complete-route/<int:route_id>', methods=['POST'])
def complete_route(route_id):
    route_model.update_route_status(route_id, 'completed')
    flash('Rota tamamlandı.', 'success')
    return redirect(url_for('driver_ui.index'))
