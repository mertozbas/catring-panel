from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import route as route_model
from models import order as order_model
from models import driver as driver_model
from datetime import date
from utils.maps import optimize_route
import config

bp = Blueprint('routes', __name__)


def _optimize_single_route(route_id):
    """Tek bir rotayı optimize et (iç fonksiyon)."""
    orders = order_model.get_orders_by_route(route_id)
    locations = []
    for o in orders:
        if o['latitude'] and o['longitude']:
            locations.append({
                'lat': o['latitude'],
                'lng': o['longitude'],
                'name': o['customer_name'],
                'order_id': o['id']
            })

    if len(locations) < 2:
        return False

    result = optimize_route(locations)
    if result.get('optimized'):
        for seq, idx in enumerate(result['order'], 1):
            if idx < len(locations):
                order_model.update_delivery_sequence(locations[idx]['order_id'], seq)

        route_model.update_route_optimization(route_id,
            result.get('total_distance_km', 0),
            result.get('total_duration_min', 0)
        )
        return True
    return False


@bp.route('/')
def index():
    selected_date = request.args.get('date', date.today().isoformat())
    routes = route_model.get_routes_by_date(selected_date)
    drivers = driver_model.get_all_drivers()
    unassigned = order_model.get_unassigned_orders(selected_date)

    route_orders = {}
    for r in routes:
        route_orders[r['id']] = order_model.get_orders_by_route(r['id'])

    return render_template('routes.html',
                           routes=routes,
                           route_orders=route_orders,
                           drivers=drivers,
                           unassigned=unassigned,
                           selected_date=selected_date)


@bp.route('/add', methods=['POST'])
def add():
    data = {
        'date': request.form.get('date'),
        'driver_id': request.form.get('driver_id'),
        'service_number': request.form.get('service_number', 1),
        'route_name': request.form.get('route_name'),
    }
    route_model.create_route(data)
    flash('Rota oluşturuldu.', 'success')
    return redirect(url_for('routes.index', date=data['date']))


@bp.route('/edit/<int:route_id>', methods=['POST'])
def edit(route_id):
    data = {
        'driver_id': request.form.get('driver_id'),
        'service_number': request.form.get('service_number', 1),
        'route_name': request.form.get('route_name'),
        'status': request.form.get('status', 'planned'),
    }
    route_model.update_route(route_id, data)
    flash('Rota güncellendi.', 'success')
    return redirect(url_for('routes.index', date=request.form.get('date', date.today().isoformat())))


@bp.route('/delete/<int:route_id>')
def delete(route_id):
    route = route_model.get_route(route_id)
    route_date = route['date'] if route else date.today().isoformat()
    route_model.delete_route(route_id)
    flash('Rota silindi.', 'success')
    return redirect(url_for('routes.index', date=route_date))


@bp.route('/assign', methods=['POST'])
def assign():
    order_id = request.form.get('order_id')
    route_id = request.form.get('route_id')
    sequence = request.form.get('delivery_sequence', 0)
    order_model.assign_order_to_route(order_id, route_id, sequence)
    route_model.update_route_totals(route_id)
    flash('Sipariş rotaya atandı.', 'success')
    return redirect(url_for('routes.index', date=request.form.get('date', date.today().isoformat())))


@bp.route('/auto-create', methods=['POST'])
def auto_create():
    """Aktif şoförler için otomatik rota oluştur."""
    selected_date = request.form.get('date', date.today().isoformat())
    created = route_model.auto_create_routes(selected_date)
    if created > 0:
        flash(f'{created} rota otomatik oluşturuldu.', 'success')
    else:
        flash('Tüm şoförler için rota zaten mevcut.', 'info')
    return redirect(url_for('routes.index', date=selected_date))


@bp.route('/auto-assign', methods=['POST'])
def auto_assign():
    """Siparişleri müşteri varsayılanlarına göre rotalara ata."""
    selected_date = request.form.get('date', date.today().isoformat())
    assigned = order_model.auto_assign_routes(selected_date)
    # Rota toplamlarını güncelle
    routes = route_model.get_routes_by_date(selected_date)
    for r in routes:
        route_model.update_route_totals(r['id'])
    # Otomatik rota optimizasyonu
    optimized_count = 0
    if assigned > 0 and config.GOOGLE_MAPS_API_KEY:
        for r in routes:
            if _optimize_single_route(r['id']):
                optimized_count += 1

    if assigned > 0:
        msg = f'{assigned} sipariş otomatik rotalara atandı.'
        if optimized_count > 0:
            msg += f' {optimized_count} rota optimize edildi.'
        flash(msg, 'success')
    else:
        flash('Atanacak sipariş bulunamadı.', 'info')
    return redirect(url_for('routes.index', date=selected_date))


@bp.route('/optimize/<int:route_id>', methods=['POST'])
def optimize(route_id):
    """Rota optimizasyonu: Google Maps ile en kısa yolu hesapla."""
    if _optimize_single_route(route_id):
        route = route_model.get_route(route_id)
        flash(f'Rota optimize edildi: {route["optimized_distance_km"]} km, ~{route["optimized_duration_min"]} dk', 'success')
    else:
        flash('Rota optimizasyonu başarısız oldu. En az 2 koordinatlı sipariş gerekli veya API key kontrol edin.', 'warning')

    return redirect(url_for('routes.index', date=request.form.get('date', date.today().isoformat())))


@bp.route('/api/<int:route_id>/orders')
def api_route_orders(route_id):
    orders = order_model.get_orders_by_route(route_id)
    return jsonify([dict(o) for o in orders])
