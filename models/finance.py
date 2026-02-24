from models.db import query_db, insert_db, update_db, get_db
from datetime import datetime


def get_all_invoices():
    return query_db(
        '''SELECT i.*, c.name as customer_name
           FROM invoices i LEFT JOIN customers c ON i.customer_id = c.id
           ORDER BY i.date DESC'''
    )


def get_invoice(invoice_id):
    return query_db(
        '''SELECT i.*, c.name as customer_name, c.address as customer_address,
                  c.phone as customer_phone, c.contact_name as customer_contact
           FROM invoices i LEFT JOIN customers c ON i.customer_id = c.id
           WHERE i.id = ?''',
        [invoice_id], one=True
    )


def create_invoice(data):
    now = datetime.now()
    inv_number = f"INV-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"
    return insert_db(
        '''INSERT INTO invoices (customer_id, invoice_number, date, period_start,
           period_end, total_portions, unit_price, total_amount, tax_amount, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        [data.get('customer_id'), inv_number, data.get('date'),
         data.get('period_start'), data.get('period_end'),
         data.get('total_portions', 0), data.get('unit_price', 0),
         data.get('total_amount', 0), data.get('tax_amount', 0),
         data.get('notes')]
    )


def update_invoice(invoice_id, data):
    return update_db(
        '''UPDATE invoices SET customer_id=?, date=?, period_start=?, period_end=?,
           total_portions=?, unit_price=?, total_amount=?, tax_amount=?, status=?, notes=?
           WHERE id=?''',
        [data.get('customer_id'), data.get('date'), data.get('period_start'),
         data.get('period_end'), data.get('total_portions', 0),
         data.get('unit_price', 0), data.get('total_amount', 0),
         data.get('tax_amount', 0), data.get('status', 'draft'),
         data.get('notes'), invoice_id]
    )


def update_invoice_status(invoice_id, status):
    return update_db('UPDATE invoices SET status=? WHERE id=?', [status, invoice_id])


def get_all_transactions(limit=100):
    return query_db('SELECT * FROM transactions ORDER BY date DESC LIMIT ?', [limit])


def get_transactions_by_period(start_date, end_date):
    return query_db(
        'SELECT * FROM transactions WHERE date BETWEEN ? AND ? ORDER BY date DESC',
        [start_date, end_date]
    )


def create_transaction(data):
    return insert_db(
        '''INSERT INTO transactions (type, category, description, amount, date, invoice_id, purchase_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        [data.get('type'), data.get('category'), data.get('description'),
         data.get('amount'), data.get('date'),
         data.get('invoice_id'), data.get('purchase_id')]
    )


def get_financial_summary(start_date, end_date):
    return query_db(
        '''SELECT
             SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as total_income,
             SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as total_expense
           FROM transactions WHERE date BETWEEN ? AND ?''',
        [start_date, end_date], one=True
    )


def get_erp_settings():
    return query_db('SELECT * FROM erp_settings WHERE id = 1', one=True)


def update_erp_settings(data):
    return update_db(
        '''UPDATE erp_settings SET erp_mode=?, external_erp_url=?,
           external_erp_api_key=?, external_erp_type=? WHERE id=1''',
        [data.get('erp_mode', 'builtin'), data.get('external_erp_url'),
         data.get('external_erp_api_key'), data.get('external_erp_type')]
    )


# ============ PAYMENT / CARİ HESAP FUNCTIONS ============

def create_payment(data):
    """Ödeme kaydı oluştur."""
    return insert_db(
        '''INSERT INTO payments (customer_id, invoice_id, amount, date, payment_method, notes)
           VALUES (?, ?, ?, ?, ?, ?)''',
        [data.get('customer_id'), data.get('invoice_id'),
         data.get('amount'), data.get('date'),
         data.get('payment_method', 'nakit'), data.get('notes')]
    )


def get_payments_by_customer(customer_id):
    """Müşterinin tüm ödemelerini getir."""
    return query_db(
        '''SELECT p.*, i.invoice_number
           FROM payments p
           LEFT JOIN invoices i ON p.invoice_id = i.id
           WHERE p.customer_id = ?
           ORDER BY p.date DESC''',
        [customer_id]
    )


def get_all_payments(limit=100):
    """Tüm ödemeleri getir."""
    return query_db(
        '''SELECT p.*, c.name as customer_name, i.invoice_number
           FROM payments p
           JOIN customers c ON p.customer_id = c.id
           LEFT JOIN invoices i ON p.invoice_id = i.id
           ORDER BY p.date DESC LIMIT ?''',
        [limit]
    )


def get_customer_balance(customer_id):
    """Müşterinin cari bakiyesini hesapla (Borç - Ödeme)."""
    result = query_db(
        '''SELECT
             COALESCE((SELECT SUM(total_amount + tax_amount) FROM invoices
                        WHERE customer_id = ? AND status != 'cancelled'), 0) as total_debt,
             COALESCE((SELECT SUM(amount) FROM payments WHERE customer_id = ?), 0) as total_paid
        ''',
        [customer_id, customer_id], one=True
    )
    return result


def get_all_customer_balances():
    """Tüm müşterilerin cari bakiyelerini getir."""
    return query_db(
        '''SELECT c.id, c.name, c.segment,
                  COALESCE(inv.total_debt, 0) as total_debt,
                  COALESCE(pay.total_paid, 0) as total_paid,
                  COALESCE(inv.total_debt, 0) - COALESCE(pay.total_paid, 0) as balance
           FROM customers c
           LEFT JOIN (
               SELECT customer_id, SUM(total_amount + tax_amount) as total_debt
               FROM invoices WHERE status != 'cancelled'
               GROUP BY customer_id
           ) inv ON c.id = inv.customer_id
           LEFT JOIN (
               SELECT customer_id, SUM(amount) as total_paid
               FROM payments GROUP BY customer_id
           ) pay ON c.id = pay.customer_id
           WHERE c.is_active = 1 AND (COALESCE(inv.total_debt, 0) > 0 OR COALESCE(pay.total_paid, 0) > 0)
           ORDER BY balance DESC'''
    )


# ============ AUTO INVOICE FUNCTIONS ============

def calculate_customer_portions(customer_id, period_start, period_end):
    """Dönem içindeki müşteri porsiyon toplamını hesapla."""
    result = query_db(
        '''SELECT COUNT(*) as order_count,
                  COALESCE(SUM(portion_count), 0) as total_portions
           FROM orders
           WHERE customer_id = ? AND date BETWEEN ? AND ?
           AND status != 'cancelled' ''',
        [customer_id, period_start, period_end], one=True
    )
    return result


def generate_auto_invoice(customer_id, period_start, period_end, unit_price, tax_rate=10):
    """Müşteri için otomatik fatura oluştur."""
    portions_data = calculate_customer_portions(customer_id, period_start, period_end)
    total_portions = portions_data['total_portions'] or 0

    if total_portions == 0:
        return None

    subtotal = total_portions * unit_price
    tax_amount = subtotal * (tax_rate / 100)
    total_amount = subtotal

    now = datetime.now()
    inv_number = f"INV-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"

    invoice_id = insert_db(
        '''INSERT INTO invoices (customer_id, invoice_number, date, period_start,
           period_end, total_portions, unit_price, total_amount, tax_amount, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        [customer_id, inv_number, now.strftime('%Y-%m-%d'),
         period_start, period_end, total_portions, unit_price,
         total_amount, tax_amount,
         f"Otomatik fatura: {period_start} - {period_end}"]
    )
    return invoice_id


# ============ COST ANALYSIS FUNCTIONS ============

def get_daily_cost_report(date_str):
    """Günlük maliyet raporu - reçete bazlı."""
    return query_db(
        '''SELECT mi.item_name, mi.category,
                  r.per_person_cost,
                  (SELECT SUM(o.portion_count) FROM orders o WHERE o.date = ?) as total_portions,
                  r.per_person_cost * (SELECT SUM(o.portion_count) FROM orders o WHERE o.date = ?) as total_cost
           FROM menu_items mi
           JOIN weekly_menus wm ON mi.weekly_menu_id = wm.id
           LEFT JOIN recipes r ON r.menu_item_name = mi.item_name
           WHERE wm.status = 'active'
           AND mi.day_of_week = (
               CASE CAST(strftime('%w', ?) AS INTEGER)
                   WHEN 0 THEN 6
                   ELSE CAST(strftime('%w', ?) AS INTEGER) - 1
               END
           )
           ORDER BY mi.item_order''',
        [date_str, date_str, date_str, date_str]
    )


def get_period_expense_breakdown(start_date, end_date):
    """Dönem gider kırılımı (kategoriye göre)."""
    return query_db(
        '''SELECT category,
                  COUNT(*) as count,
                  SUM(amount) as total
           FROM transactions
           WHERE type = 'expense' AND date BETWEEN ? AND ?
           GROUP BY category
           ORDER BY total DESC''',
        [start_date, end_date]
    )


def get_period_comparison(current_start, current_end, prev_start, prev_end):
    """İki dönemi karşılaştır (gelir, gider, sipariş)."""
    current = query_db(
        '''SELECT
             COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as income,
             COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as expense
           FROM transactions WHERE date BETWEEN ? AND ?''',
        [current_start, current_end], one=True
    )
    previous = query_db(
        '''SELECT
             COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as income,
             COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as expense
           FROM transactions WHERE date BETWEEN ? AND ?''',
        [prev_start, prev_end], one=True
    )
    current_orders = query_db(
        '''SELECT COUNT(*) as count, COALESCE(SUM(portion_count),0) as portions
           FROM orders WHERE date BETWEEN ? AND ? AND status != 'cancelled' ''',
        [current_start, current_end], one=True
    )
    prev_orders = query_db(
        '''SELECT COUNT(*) as count, COALESCE(SUM(portion_count),0) as portions
           FROM orders WHERE date BETWEEN ? AND ? AND status != 'cancelled' ''',
        [prev_start, prev_end], one=True
    )
    return {
        'current': {
            'income': current['income'] or 0,
            'expense': current['expense'] or 0,
            'orders': current_orders['count'] or 0,
            'portions': current_orders['portions'] or 0,
        },
        'previous': {
            'income': previous['income'] or 0,
            'expense': previous['expense'] or 0,
            'orders': prev_orders['count'] or 0,
            'portions': prev_orders['portions'] or 0,
        }
    }


def get_monthly_trend(months=6):
    """Son N aylık gelir/gider trendi."""
    return query_db(
        '''SELECT strftime('%Y-%m', date) as month,
                  SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as income,
                  SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as expense
           FROM transactions
           WHERE date >= date('now', ?)
           GROUP BY strftime('%Y-%m', date)
           ORDER BY month''',
        [f'-{months} months']
    )


def get_unpaid_invoices():
    """Ödenmemiş faturaları getir."""
    return query_db(
        '''SELECT i.*, c.name as customer_name
           FROM invoices i
           LEFT JOIN customers c ON i.customer_id = c.id
           WHERE i.status IN ('draft', 'sent')
           ORDER BY i.date ASC'''
    )
