from flask import Blueprint, render_template
from models.db import query_db
from datetime import date

bp = Blueprint('dashboard', __name__)


@bp.route('/dashboard')
def index():
    today = date.today().isoformat()

    total_customers = query_db('SELECT COUNT(*) as c FROM customers WHERE is_active=1', one=True)['c']
    total_drivers = query_db('SELECT COUNT(*) as c FROM drivers WHERE is_active=1', one=True)['c']

    daily = query_db(
        '''SELECT COUNT(*) as total_orders, COALESCE(SUM(portion_count),0) as total_portions
           FROM orders WHERE date=?''', [today], one=True)

    routes_today = query_db('SELECT COUNT(*) as c FROM routes WHERE date=?', [today], one=True)['c']

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
                           recent_orders=recent_orders)
