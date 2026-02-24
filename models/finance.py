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
        '''SELECT i.*, c.name as customer_name
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
