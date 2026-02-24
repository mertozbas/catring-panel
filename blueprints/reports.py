from flask import Blueprint, render_template, request, Response, session
from models.db import query_db, get_db
from models import customer as customer_model
from models import driver as driver_model
from datetime import date, timedelta
import csv
import io

bp = Blueprint('reports', __name__)


def get_daily_report(date_str):
    """Gunluk rapor verileri."""
    db = get_db()

    # Siparis ozeti
    orders_summary = db.execute(
        '''SELECT
             COUNT(*) as total_orders,
             COALESCE(SUM(portion_count), 0) as total_portions,
             SUM(CASE WHEN status='delivered' THEN 1 ELSE 0 END) as delivered,
             SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) as pending,
             SUM(CASE WHEN status='preparing' THEN 1 ELSE 0 END) as preparing,
             SUM(CASE WHEN status='ready' THEN 1 ELSE 0 END) as ready,
             SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) as cancelled
           FROM orders WHERE date = ?''',
        [date_str]
    ).fetchone()

    # Kap tipi dagilimi
    container_breakdown = db.execute(
        '''SELECT container_type,
                  COUNT(*) as count,
                  SUM(portion_count) as portions
           FROM orders WHERE date = ?
           GROUP BY container_type
           ORDER BY portions DESC''',
        [date_str]
    ).fetchall()

    # Rota ozeti
    route_summary = db.execute(
        '''SELECT r.id, r.route_name, d.name as driver_name, r.status,
                  r.total_portions, r.optimized_distance_km, r.optimized_duration_min,
                  COUNT(o.id) as order_count,
                  SUM(CASE WHEN o.status='delivered' THEN 1 ELSE 0 END) as delivered_count
           FROM routes r
           JOIN drivers d ON r.driver_id = d.id
           LEFT JOIN orders o ON o.route_id = r.id
           WHERE r.date = ?
           GROUP BY r.id
           ORDER BY d.name''',
        [date_str]
    ).fetchall()

    # Musteri bazli siparis listesi
    customer_orders = db.execute(
        '''SELECT o.*, c.name as customer_name, c.segment,
                  r.route_name
           FROM orders o
           JOIN customers c ON o.customer_id = c.id
           LEFT JOIN routes r ON o.route_id = r.id
           WHERE o.date = ?
           ORDER BY c.name''',
        [date_str]
    ).fetchall()

    # Problemler
    problems = db.execute(
        '''SELECT dc.*, o.date, c.name as customer_name, d.name as driver_name
           FROM delivery_confirmations dc
           JOIN orders o ON dc.order_id = o.id
           JOIN customers c ON o.customer_id = c.id
           LEFT JOIN drivers d ON dc.driver_id = d.id
           WHERE o.date = ? AND dc.problem_type IS NOT NULL
           ORDER BY dc.delivered_at DESC''',
        [date_str]
    ).fetchall()

    return {
        'summary': dict(orders_summary),
        'container_breakdown': [dict(r) for r in container_breakdown],
        'route_summary': [dict(r) for r in route_summary],
        'customer_orders': [dict(r) for r in customer_orders],
        'problems': [dict(r) for r in problems],
    }


def get_weekly_report(start_date, end_date):
    """Haftalik rapor verileri."""
    db = get_db()

    # Gunluk porsiyon trendi
    daily_trend = db.execute(
        '''SELECT date,
                  COUNT(*) as order_count,
                  COALESCE(SUM(portion_count), 0) as total_portions,
                  SUM(CASE WHEN status='delivered' THEN 1 ELSE 0 END) as delivered,
                  SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) as cancelled
           FROM orders
           WHERE date BETWEEN ? AND ?
           GROUP BY date
           ORDER BY date''',
        [start_date, end_date]
    ).fetchall()

    # Musteri dagilimi (en cok siparis verenler)
    top_customers = db.execute(
        '''SELECT c.name, c.segment,
                  COUNT(*) as order_count,
                  SUM(o.portion_count) as total_portions
           FROM orders o
           JOIN customers c ON o.customer_id = c.id
           WHERE o.date BETWEEN ? AND ? AND o.status != 'cancelled'
           GROUP BY c.id
           ORDER BY total_portions DESC
           LIMIT 20''',
        [start_date, end_date]
    ).fetchall()

    # Kap tipi haftalik ozet
    container_weekly = db.execute(
        '''SELECT container_type,
                  COUNT(*) as count,
                  SUM(portion_count) as portions
           FROM orders
           WHERE date BETWEEN ? AND ? AND status != 'cancelled'
           GROUP BY container_type
           ORDER BY portions DESC''',
        [start_date, end_date]
    ).fetchall()

    # Toplam istatistikler
    totals = db.execute(
        '''SELECT
             COUNT(*) as total_orders,
             COALESCE(SUM(portion_count), 0) as total_portions,
             SUM(CASE WHEN status='delivered' THEN 1 ELSE 0 END) as delivered,
             SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) as cancelled,
             COUNT(DISTINCT customer_id) as unique_customers
           FROM orders
           WHERE date BETWEEN ? AND ?''',
        [start_date, end_date]
    ).fetchone()

    # Finansal ozet
    financial = db.execute(
        '''SELECT
             COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as income,
             COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as expense
           FROM transactions
           WHERE date BETWEEN ? AND ?''',
        [start_date, end_date]
    ).fetchone()

    return {
        'daily_trend': [dict(r) for r in daily_trend],
        'top_customers': [dict(r) for r in top_customers],
        'container_weekly': [dict(r) for r in container_weekly],
        'totals': dict(totals),
        'financial': dict(financial),
    }


def get_customer_report(customer_id, start_date, end_date):
    """Musteri raporu."""
    db = get_db()

    customer = customer_model.get_customer(customer_id)
    if not customer:
        return None

    # Siparis gecmisi
    orders = db.execute(
        '''SELECT o.*, r.route_name
           FROM orders o
           LEFT JOIN routes r ON o.route_id = r.id
           WHERE o.customer_id = ? AND o.date BETWEEN ? AND ?
           ORDER BY o.date DESC''',
        [customer_id, start_date, end_date]
    ).fetchall()

    # Istatistikler
    stats = db.execute(
        '''SELECT
             COUNT(*) as total_orders,
             COALESCE(SUM(portion_count), 0) as total_portions,
             ROUND(AVG(portion_count), 1) as avg_portions,
             SUM(CASE WHEN status='delivered' THEN 1 ELSE 0 END) as delivered,
             SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) as cancelled
           FROM orders
           WHERE customer_id = ? AND date BETWEEN ? AND ?''',
        [customer_id, start_date, end_date]
    ).fetchone()

    # Gunluk porsiyon trendi
    daily = db.execute(
        '''SELECT date, SUM(portion_count) as portions
           FROM orders
           WHERE customer_id = ? AND date BETWEEN ? AND ? AND status != 'cancelled'
           GROUP BY date ORDER BY date''',
        [customer_id, start_date, end_date]
    ).fetchall()

    # Odeme gecmisi
    payments = db.execute(
        '''SELECT p.*, i.invoice_number
           FROM payments p
           LEFT JOIN invoices i ON p.invoice_id = i.id
           WHERE p.customer_id = ?
           ORDER BY p.date DESC LIMIT 20''',
        [customer_id]
    ).fetchall()

    # Bakiye
    balance = db.execute(
        '''SELECT
             COALESCE((SELECT SUM(total_amount + tax_amount) FROM invoices
                        WHERE customer_id = ? AND status != 'cancelled'), 0) as total_debt,
             COALESCE((SELECT SUM(amount) FROM payments WHERE customer_id = ?), 0) as total_paid
        ''',
        [customer_id, customer_id]
    ).fetchone()

    return {
        'customer': dict(customer),
        'orders': [dict(r) for r in orders],
        'stats': dict(stats),
        'daily': [dict(r) for r in daily],
        'payments': [dict(r) for r in payments],
        'balance': dict(balance),
    }


def get_stock_report():
    """Stok raporu."""
    db = get_db()

    # Tum stok
    all_stock = db.execute(
        '''SELECT * FROM inventory ORDER BY ingredient_name'''
    ).fetchall()

    # Dusuk stoklar
    low_stock = db.execute(
        '''SELECT * FROM inventory
           WHERE current_stock < min_stock_level AND min_stock_level > 0
           ORDER BY (current_stock / NULLIF(min_stock_level, 0))'''
    ).fetchall()

    # Son 7 gun tuketim
    consumption = db.execute(
        '''SELECT i.ingredient_name, i.unit,
                  SUM(it.quantity) as consumed_7d
           FROM inventory_transactions it
           JOIN inventory i ON it.inventory_id = i.id
           WHERE it.type = 'out' AND it.created_at >= date('now', '-7 days')
           GROUP BY it.inventory_id
           ORDER BY consumed_7d DESC'''
    ).fetchall()

    # Son 7 gun giris
    incoming = db.execute(
        '''SELECT i.ingredient_name, i.unit,
                  SUM(it.quantity) as received_7d
           FROM inventory_transactions it
           JOIN inventory i ON it.inventory_id = i.id
           WHERE it.type = 'in' AND it.created_at >= date('now', '-7 days')
           GROUP BY it.inventory_id
           ORDER BY received_7d DESC'''
    ).fetchall()

    return {
        'all_stock': [dict(r) for r in all_stock],
        'low_stock': [dict(r) for r in low_stock],
        'consumption': [dict(r) for r in consumption],
        'incoming': [dict(r) for r in incoming],
    }


def get_driver_performance(start_date, end_date):
    """Sofor performans raporu."""
    db = get_db()

    drivers = db.execute(
        '''SELECT d.id, d.name,
                  COUNT(DISTINCT r.id) as route_count,
                  COUNT(o.id) as total_orders,
                  SUM(CASE WHEN o.status='delivered' THEN 1 ELSE 0 END) as delivered,
                  SUM(CASE WHEN o.status='cancelled' THEN 1 ELSE 0 END) as cancelled,
                  COALESCE(SUM(o.portion_count), 0) as total_portions,
                  SUM(r.optimized_distance_km) as total_km,
                  SUM(CASE WHEN r.status='completed' THEN 1 ELSE 0 END) as completed_routes
           FROM drivers d
           LEFT JOIN routes r ON d.id = r.driver_id AND r.date BETWEEN ? AND ?
           LEFT JOIN orders o ON o.route_id = r.id
           WHERE d.is_active = 1
           GROUP BY d.id
           ORDER BY total_portions DESC''',
        [start_date, end_date]
    ).fetchall()

    # Gunluk sofor detay
    daily_driver = db.execute(
        '''SELECT r.date, d.name as driver_name,
                  r.total_portions, r.status as route_status,
                  COUNT(o.id) as order_count,
                  SUM(CASE WHEN o.status='delivered' THEN 1 ELSE 0 END) as delivered
           FROM routes r
           JOIN drivers d ON r.driver_id = d.id
           LEFT JOIN orders o ON o.route_id = r.id
           WHERE r.date BETWEEN ? AND ?
           GROUP BY r.id
           ORDER BY r.date DESC, d.name''',
        [start_date, end_date]
    ).fetchall()

    # Problem istatistikleri
    problems = db.execute(
        '''SELECT d.name as driver_name,
                  dc.problem_type,
                  COUNT(*) as count
           FROM delivery_confirmations dc
           JOIN orders o ON dc.order_id = o.id
           JOIN routes r ON o.route_id = r.id
           JOIN drivers d ON dc.driver_id = d.id
           WHERE o.date BETWEEN ? AND ? AND dc.problem_type IS NOT NULL
           GROUP BY d.id, dc.problem_type
           ORDER BY count DESC''',
        [start_date, end_date]
    ).fetchall()

    return {
        'drivers': [dict(r) for r in drivers],
        'daily_driver': [dict(r) for r in daily_driver],
        'problems': [dict(r) for r in problems],
    }


@bp.route('/')
def index():
    tab = request.args.get('tab', 'daily')
    today = date.today()

    # Varsayilan tarihler
    report_date = request.args.get('date', today.isoformat())

    # Haftalik icin
    week_start = request.args.get('week_start', (today - timedelta(days=today.weekday())).isoformat())
    week_end = request.args.get('week_end', (today - timedelta(days=today.weekday()) + timedelta(days=6)).isoformat())

    # Musteri raporu icin
    customer_id = request.args.get('customer_id', type=int)
    period_start = request.args.get('period_start', (today.replace(day=1)).isoformat())
    period_end = request.args.get('period_end', today.isoformat())

    # Sofor raporu icin
    driver_start = request.args.get('driver_start', (today - timedelta(days=today.weekday())).isoformat())
    driver_end = request.args.get('driver_end', today.isoformat())

    # Tab verileri
    daily_data = None
    weekly_data = None
    customer_data = None
    stock_data = None
    driver_data = None

    if tab == 'daily':
        daily_data = get_daily_report(report_date)
    elif tab == 'weekly':
        weekly_data = get_weekly_report(week_start, week_end)
    elif tab == 'customer':
        if customer_id:
            customer_data = get_customer_report(customer_id, period_start, period_end)
    elif tab == 'stock':
        stock_data = get_stock_report()
    elif tab == 'driver':
        driver_data = get_driver_performance(driver_start, driver_end)

    customers = customer_model.get_all_customers()

    return render_template('reports.html',
                           tab=tab,
                           report_date=report_date,
                           week_start=week_start,
                           week_end=week_end,
                           customer_id=customer_id,
                           period_start=period_start,
                           period_end=period_end,
                           driver_start=driver_start,
                           driver_end=driver_end,
                           daily_data=daily_data,
                           weekly_data=weekly_data,
                           customer_data=customer_data,
                           stock_data=stock_data,
                           driver_data=driver_data,
                           customers=customers)


@bp.route('/export/<report_type>')
def export_csv(report_type):
    """CSV export endpoint."""
    today = date.today()

    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'daily':
        report_date = request.args.get('date', today.isoformat())
        data = get_daily_report(report_date)
        filename = f"gunluk_rapor_{report_date}.csv"

        writer.writerow(['Musteri', 'Porsiyon', 'Kap Tipi', 'Durum', 'Rota', 'Ozel Not'])
        for o in data['customer_orders']:
            writer.writerow([
                o['customer_name'], o['portion_count'],
                o.get('container_type', ''), o['status'],
                o.get('route_name', ''), o.get('special_notes', '')
            ])

    elif report_type == 'weekly':
        week_start = request.args.get('week_start', (today - timedelta(days=today.weekday())).isoformat())
        week_end = request.args.get('week_end', (today - timedelta(days=today.weekday()) + timedelta(days=6)).isoformat())
        data = get_weekly_report(week_start, week_end)
        filename = f"haftalik_rapor_{week_start}_{week_end}.csv"

        writer.writerow(['Tarih', 'Siparis Sayisi', 'Toplam Porsiyon', 'Teslim Edilen', 'Iptal'])
        for d in data['daily_trend']:
            writer.writerow([
                d['date'], d['order_count'], d['total_portions'],
                d['delivered'], d['cancelled']
            ])
        writer.writerow([])
        writer.writerow(['--- En Cok Siparis Veren Musteriler ---'])
        writer.writerow(['Musteri', 'Segment', 'Siparis Sayisi', 'Toplam Porsiyon'])
        for c in data['top_customers']:
            writer.writerow([
                c['name'], c.get('segment', ''), c['order_count'], c['total_portions']
            ])

    elif report_type == 'customer':
        customer_id = request.args.get('customer_id', type=int)
        period_start = request.args.get('period_start', today.replace(day=1).isoformat())
        period_end = request.args.get('period_end', today.isoformat())
        if not customer_id:
            return 'Musteri secilmedi', 400
        data = get_customer_report(customer_id, period_start, period_end)
        if not data:
            return 'Musteri bulunamadi', 404
        filename = f"musteri_rapor_{data['customer']['name']}_{period_start}_{period_end}.csv"

        writer.writerow([f"Musteri: {data['customer']['name']}"])
        writer.writerow([f"Donem: {period_start} - {period_end}"])
        writer.writerow([f"Toplam Siparis: {data['stats']['total_orders']}", f"Toplam Porsiyon: {data['stats']['total_portions']}"])
        writer.writerow([])
        writer.writerow(['Tarih', 'Porsiyon', 'Kap Tipi', 'Durum', 'Rota', 'Not'])
        for o in data['orders']:
            writer.writerow([
                o['date'], o['portion_count'], o.get('container_type', ''),
                o['status'], o.get('route_name', ''), o.get('special_notes', '')
            ])

    elif report_type == 'stock':
        data = get_stock_report()
        filename = f"stok_rapor_{today.isoformat()}.csv"

        writer.writerow(['Malzeme', 'Mevcut Stok', 'Min Stok', 'Birim', 'Durum'])
        for s in data['all_stock']:
            status = 'DUSUK' if s.get('min_stock_level') and s['current_stock'] < s['min_stock_level'] else 'Normal'
            writer.writerow([
                s['ingredient_name'], s['current_stock'],
                s.get('min_stock_level', 0), s['unit'], status
            ])
        writer.writerow([])
        writer.writerow(['--- Son 7 Gun Tuketim ---'])
        writer.writerow(['Malzeme', 'Birim', 'Tuketim (7 gun)'])
        for c in data['consumption']:
            writer.writerow([c['ingredient_name'], c['unit'], c['consumed_7d']])

    elif report_type == 'driver':
        driver_start = request.args.get('driver_start', (today - timedelta(days=today.weekday())).isoformat())
        driver_end = request.args.get('driver_end', today.isoformat())
        data = get_driver_performance(driver_start, driver_end)
        filename = f"sofor_performans_{driver_start}_{driver_end}.csv"

        writer.writerow(['Sofor', 'Rota Sayisi', 'Siparis', 'Teslim', 'Iptal', 'Porsiyon', 'Toplam KM', 'Tamamlanan Rota'])
        for d in data['drivers']:
            writer.writerow([
                d['name'], d['route_count'], d['total_orders'],
                d['delivered'], d['cancelled'], d['total_portions'],
                d.get('total_km', '-'), d['completed_routes']
            ])
    else:
        return 'Gecersiz rapor tipi', 400

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': 'text/csv; charset=utf-8-sig'
        }
    )
