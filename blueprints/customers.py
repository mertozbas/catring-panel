from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import customer as customer_model
from utils.maps import geocode_address
import config

bp = Blueprint('customers', __name__)


@bp.route('/')
def index():
    q = request.args.get('q', '')
    if q:
        customers = customer_model.search_customers(q)
    else:
        customers = customer_model.get_all_customers()
    return render_template('customers.html', customers=customers, q=q, google_maps_key=config.GOOGLE_MAPS_API_KEY)


@bp.route('/add', methods=['POST'])
def add():
    data = {
        'name': request.form.get('name'),
        'contact_name': request.form.get('contact_name'),
        'phone': request.form.get('phone'),
        'telegram_chat_id': request.form.get('telegram_chat_id'),
        'address': request.form.get('address'),
        'latitude': request.form.get('latitude') or None,
        'longitude': request.form.get('longitude') or None,
        'default_variety_count': request.form.get('default_variety_count', 4),
        'default_container_type': request.form.get('default_container_type', 'sefer_tasi'),
        'default_portion_count': request.form.get('default_portion_count') or None,
        'special_notes': request.form.get('special_notes'),
    }
    # Otomatik geocoding: adres var ama koordinat yoksa
    if not data['latitude'] and data.get('address'):
        lat, lng = geocode_address(data['address'])
        if lat and lng:
            data['latitude'] = lat
            data['longitude'] = lng
            flash('Koordinatlar adresten otomatik hesaplandı.', 'info')
    customer_model.create_customer(data)
    flash('Müşteri başarıyla eklendi.', 'success')
    return redirect(url_for('customers.index'))


@bp.route('/edit/<int:customer_id>', methods=['POST'])
def edit(customer_id):
    data = {
        'name': request.form.get('name'),
        'contact_name': request.form.get('contact_name'),
        'phone': request.form.get('phone'),
        'telegram_chat_id': request.form.get('telegram_chat_id'),
        'address': request.form.get('address'),
        'latitude': request.form.get('latitude') or None,
        'longitude': request.form.get('longitude') or None,
        'default_variety_count': request.form.get('default_variety_count', 4),
        'default_container_type': request.form.get('default_container_type', 'sefer_tasi'),
        'default_portion_count': request.form.get('default_portion_count') or None,
        'special_notes': request.form.get('special_notes'),
    }
    # Otomatik geocoding: adres var ama koordinat yoksa
    if not data['latitude'] and data.get('address'):
        lat, lng = geocode_address(data['address'])
        if lat and lng:
            data['latitude'] = lat
            data['longitude'] = lng
            flash('Koordinatlar adresten otomatik hesaplandı.', 'info')
    customer_model.update_customer(customer_id, data)
    flash('Müşteri güncellendi.', 'success')
    return redirect(url_for('customers.index'))


@bp.route('/toggle/<int:customer_id>/<int:active>')
def toggle(customer_id, active):
    customer_model.toggle_customer(customer_id, active)
    flash('Müşteri durumu güncellendi.', 'success')
    return redirect(url_for('customers.index'))


@bp.route('/api/search')
def api_search():
    q = request.args.get('q', '')
    customers = customer_model.search_customers(q) if q else customer_model.get_all_customers()
    return jsonify([dict(c) for c in customers])
