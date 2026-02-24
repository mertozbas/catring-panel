from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import order as order_model
from models import customer as customer_model
from models import route as route_model
from datetime import date

bp = Blueprint('orders', __name__)

CONTAINER_TYPES = [
    ('sefer_tasi', 'Sefer Tası'),
    ('paket', 'Paket'),
    ('kuvet', 'Küvet'),
    ('tepsi', 'Tepsi'),
    ('poset', 'Poşet'),
]


@bp.route('/')
def index():
    selected_date = request.args.get('date', date.today().isoformat())
    orders = order_model.get_orders_by_date(selected_date)
    customers = customer_model.get_all_customers()
    routes = route_model.get_routes_by_date(selected_date)
    summary = order_model.get_daily_summary(selected_date)
    return render_template('orders.html',
                           orders=orders,
                           customers=customers,
                           routes=routes,
                           selected_date=selected_date,
                           summary=summary,
                           container_types=CONTAINER_TYPES)


@bp.route('/add', methods=['POST'])
def add():
    data = {
        'date': request.form.get('date'),
        'customer_id': request.form.get('customer_id'),
        'route_id': request.form.get('route_id') or None,
        'delivery_sequence': request.form.get('delivery_sequence') or None,
        'variety_count': request.form.get('variety_count', 4),
        'portion_count': request.form.get('portion_count'),
        'portion_detail': request.form.get('portion_detail'),
        'container_type': request.form.get('container_type', 'sefer_tasi'),
        'special_notes': request.form.get('special_notes'),
        'extra_items': request.form.get('extra_items'),
        'cutlery_needed': 1 if request.form.get('cutlery_needed') else 0,
    }
    order_model.create_order(data)
    if data['route_id']:
        route_model.update_route_totals(data['route_id'])
    flash('Sipariş eklendi.', 'success')
    return redirect(url_for('orders.index', date=data['date']))


@bp.route('/edit/<int:order_id>', methods=['POST'])
def edit(order_id):
    old_order = order_model.get_order(order_id)
    data = {
        'customer_id': request.form.get('customer_id'),
        'route_id': request.form.get('route_id') or None,
        'delivery_sequence': request.form.get('delivery_sequence') or None,
        'variety_count': request.form.get('variety_count', 4),
        'portion_count': request.form.get('portion_count'),
        'portion_detail': request.form.get('portion_detail'),
        'container_type': request.form.get('container_type', 'sefer_tasi'),
        'special_notes': request.form.get('special_notes'),
        'extra_items': request.form.get('extra_items'),
        'cutlery_needed': 1 if request.form.get('cutlery_needed') else 0,
        'status': request.form.get('status', 'pending'),
    }
    order_model.update_order(order_id, data)
    if old_order and old_order['route_id']:
        route_model.update_route_totals(old_order['route_id'])
    if data['route_id']:
        route_model.update_route_totals(data['route_id'])
    flash('Sipariş güncellendi.', 'success')
    return redirect(url_for('orders.index', date=request.form.get('date', date.today().isoformat())))


@bp.route('/delete/<int:order_id>')
def delete(order_id):
    order = order_model.get_order(order_id)
    order_date = order['date'] if order else date.today().isoformat()
    route_id = order['route_id'] if order else None
    order_model.delete_order(order_id)
    if route_id:
        route_model.update_route_totals(route_id)
    flash('Sipariş silindi.', 'success')
    return redirect(url_for('orders.index', date=order_date))


@bp.route('/generate-daily', methods=['POST'])
def generate_daily():
    """Aktif müşteriler için günlük sipariş toplu oluştur."""
    selected_date = request.form.get('date', date.today().isoformat())
    created = order_model.generate_daily_orders(selected_date)
    if created > 0:
        flash(f'{created} müşteri için sipariş otomatik oluşturuldu.', 'success')
    else:
        flash('Tüm aktif müşteriler için sipariş zaten mevcut.', 'info')
    return redirect(url_for('orders.index', date=selected_date))


@bp.route('/api/daily-summary/<date_str>')
def api_daily_summary(date_str):
    summary = order_model.get_daily_summary(date_str)
    return jsonify(dict(summary) if summary else {})
