from flask import Blueprint, request, jsonify, session
from models import customer as customer_model
from models import order as order_model
from models import menu as menu_model
from models import route as route_model
from models import notification as notif_model
from models import inventory as inventory_model
from datetime import date

bp = Blueprint('api', __name__)


@bp.route('/customers', methods=['GET'])
def get_customers():
    customers = customer_model.get_all_customers()
    return jsonify([dict(c) for c in customers])


@bp.route('/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    cid = customer_model.create_customer(data)
    return jsonify({'id': cid, 'status': 'created'})


@bp.route('/customers/search')
def search_customers():
    q = request.args.get('q', '')
    customers = customer_model.search_customers(q)
    return jsonify([dict(c) for c in customers])


@bp.route('/orders', methods=['GET'])
def get_orders():
    d = request.args.get('date', date.today().isoformat())
    orders = order_model.get_orders_by_date(d)
    return jsonify([dict(o) for o in orders])


@bp.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    oid = order_model.create_order(data)
    if data.get('route_id'):
        route_model.update_route_totals(data['route_id'])
    return jsonify({'id': oid, 'status': 'created'})


@bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.get_json()
    order_model.update_order_status(order_id, data.get('status'))
    return jsonify({'status': 'updated'})


@bp.route('/menu/current')
def current_menu():
    menu = menu_model.get_current_week_menu()
    if not menu:
        return jsonify({'error': 'Aktif menü bulunamadı'}), 404
    items = menu_model.get_menu_items(menu['id'])
    day_names = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi']
    result = {
        'week_start_date': menu['week_start_date'],
        'status': menu['status'],
        'days': {}
    }
    for item in items:
        day = day_names[item['day_of_week']]
        if day not in result['days']:
            result['days'][day] = []
        result['days'][day].append(item['item_name'])
    return jsonify(result)


@bp.route('/routes', methods=['GET'])
def get_routes():
    d = request.args.get('date', date.today().isoformat())
    routes = route_model.get_routes_by_date(d)
    return jsonify([dict(r) for r in routes])


@bp.route('/summary/<date_str>')
def daily_summary(date_str):
    summary = order_model.get_daily_summary(date_str)
    return jsonify(dict(summary) if summary else {})


@bp.route('/inventory')
def get_inventory():
    """Stok listesi."""
    items = inventory_model.get_all_inventory()
    return jsonify([dict(i) for i in items])


@bp.route('/inventory/low-stock')
def get_low_stock():
    """Dusuk stok uyarilari."""
    items = inventory_model.get_low_stock_items()
    return jsonify([dict(i) for i in items])


@bp.route('/notifications')
def get_notifications():
    """Bildirimleri getir (AJAX polling)."""
    role = session.get('user_role', 'admin')
    # Otomatik bildirim kontrolü
    notif_model.check_and_create_notifications()
    # Bildirimleri getir
    notifications = notif_model.get_recent_notifications(15, role)
    unread_count = notif_model.get_unread_count(role)
    return jsonify({
        'unread_count': unread_count,
        'notifications': [{
            'id': n['id'],
            'type': n['type'],
            'title': n['title'],
            'message': n['message'],
            'link': n['link'],
            'is_read': n['is_read'],
            'icon': notif_model.get_notification_icon(n['type']),
            'created_at': n['created_at'],
        } for n in notifications]
    })


@bp.route('/notifications/read-all', methods=['POST'])
def mark_all_notifications_read():
    """Tüm bildirimleri okundu işaretle."""
    role = session.get('user_role', 'admin')
    notif_model.mark_all_read(role)
    return jsonify({'status': 'ok'})


@bp.route('/notifications/<int:notif_id>/read', methods=['POST'])
def mark_notification_read(notif_id):
    """Tek bildirimi okundu işaretle."""
    notif_model.mark_as_read(notif_id)
    return jsonify({'status': 'ok'})
