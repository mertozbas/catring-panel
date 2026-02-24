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
        'segment': request.form.get('segment', 'normal'),
        'unit_price': request.form.get('unit_price') or None,
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
        'segment': request.form.get('segment', 'normal'),
        'unit_price': request.form.get('unit_price') or None,
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


@bp.route('/csv-template')
def csv_template():
    """CSV template dosyası indir."""
    import io
    output = io.StringIO()
    output.write('Firma Adı,İletişim Kişisi,Telefon,Adres,Varsayılan Çeşit,Varsayılan Kap,Varsayılan Porsiyon,Özel Notlar,Segment\n')
    output.write('Örnek Firma A.Ş.,Ali Bey,0555-111-2233,"Kızılay, Ankara",4,sefer_tasi,5,Bol kepçe,normal\n')

    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=musteri_sablonu.csv'}
    )


@bp.route('/import-csv', methods=['POST'])
def import_csv():
    """CSV'den toplu müşteri import et."""
    import csv
    import io

    file = request.files.get('csv_file')
    if not file or not file.filename.endswith('.csv'):
        flash('Lütfen bir CSV dosyası seçin.', 'danger')
        return redirect(url_for('customers.index'))

    try:
        content = file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(content))

        imported = 0
        errors = []
        for i, row in enumerate(reader, start=2):
            name = row.get('Firma Adı', '').strip()
            if not name:
                errors.append(f'Satır {i}: Firma adı boş')
                continue

            container = row.get('Varsayılan Kap', 'sefer_tasi').strip()
            if container not in ('sefer_tasi', 'paket', 'kuvet', 'tepsi', 'poset'):
                container = 'sefer_tasi'

            segment = row.get('Segment', 'normal').strip().lower()
            if segment not in ('vip', 'normal', 'yeni'):
                segment = 'normal'

            data = {
                'name': name,
                'contact_name': row.get('İletişim Kişisi', '').strip() or None,
                'phone': row.get('Telefon', '').strip() or None,
                'address': row.get('Adres', '').strip() or None,
                'default_variety_count': int(row.get('Varsayılan Çeşit', 4) or 4),
                'default_container_type': container,
                'default_portion_count': int(row.get('Varsayılan Porsiyon', 0) or 0) or None,
                'special_notes': row.get('Özel Notlar', '').strip() or None,
                'segment': segment,
            }

            # Geocode if address provided
            if data['address']:
                lat, lng = geocode_address(data['address'])
                if lat and lng:
                    data['latitude'] = lat
                    data['longitude'] = lng

            customer_model.create_customer(data)
            imported += 1

        if imported > 0:
            flash(f'{imported} müşteri başarıyla içe aktarıldı.', 'success')
        if errors:
            flash(f'{len(errors)} satırda hata: {"; ".join(errors[:3])}', 'warning')
    except Exception as e:
        flash(f'CSV okuma hatası: {str(e)}', 'danger')

    return redirect(url_for('customers.index'))


@bp.route('/<int:customer_id>/history')
def history(customer_id):
    """Müşteri sipariş geçmişi."""
    customer = customer_model.get_customer(customer_id)
    if not customer:
        flash('Müşteri bulunamadı.', 'danger')
        return redirect(url_for('customers.index'))

    from models.db import query_db
    orders = query_db(
        '''SELECT o.*, r.route_name
           FROM orders o
           LEFT JOIN routes r ON o.route_id = r.id
           WHERE o.customer_id = ?
           ORDER BY o.date DESC LIMIT 90''',
        [customer_id]
    )

    stats = query_db(
        '''SELECT COUNT(*) as total_orders,
                  COALESCE(SUM(portion_count),0) as total_portions,
                  MIN(date) as first_order,
                  MAX(date) as last_order,
                  ROUND(AVG(portion_count),1) as avg_portions
           FROM orders WHERE customer_id = ?''',
        [customer_id], one=True
    )

    return render_template('customer_history.html',
                           customer=customer,
                           orders=orders,
                           stats=stats)
