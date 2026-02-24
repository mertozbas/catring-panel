from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import finance as finance_model
from models import customer as customer_model
from datetime import date, timedelta

bp = Blueprint('erp', __name__)


@bp.route('/')
def index():
    tab = request.args.get('tab', 'overview')

    today = date.today()
    month_start = today.replace(day=1).isoformat()
    month_end = today.isoformat()

    summary = finance_model.get_financial_summary(month_start, month_end)
    recent_transactions = finance_model.get_all_transactions(20)
    invoices = finance_model.get_all_invoices()
    customers = customer_model.get_all_customers()
    erp_settings = finance_model.get_erp_settings()

    return render_template('erp.html',
                           tab=tab,
                           summary=summary,
                           recent_transactions=recent_transactions,
                           invoices=invoices,
                           customers=customers,
                           erp_settings=erp_settings,
                           month_start=month_start,
                           month_end=month_end)


@bp.route('/invoices/add', methods=['POST'])
def add_invoice():
    data = {
        'customer_id': request.form.get('customer_id'),
        'date': request.form.get('date'),
        'period_start': request.form.get('period_start'),
        'period_end': request.form.get('period_end'),
        'total_portions': request.form.get('total_portions', 0),
        'unit_price': request.form.get('unit_price', 0),
        'total_amount': request.form.get('total_amount', 0),
        'tax_amount': request.form.get('tax_amount', 0),
        'notes': request.form.get('notes'),
    }
    finance_model.create_invoice(data)
    flash('Fatura oluşturuldu.', 'success')
    return redirect(url_for('erp.index', tab='invoices'))


@bp.route('/invoices/<int:invoice_id>/status/<status>')
def update_invoice_status(invoice_id, status):
    finance_model.update_invoice_status(invoice_id, status)
    flash('Fatura durumu güncellendi.', 'success')
    return redirect(url_for('erp.index', tab='invoices'))


@bp.route('/transactions/add', methods=['POST'])
def add_transaction():
    data = {
        'type': request.form.get('type'),
        'category': request.form.get('category'),
        'description': request.form.get('description'),
        'amount': float(request.form.get('amount', 0)),
        'date': request.form.get('date'),
    }
    finance_model.create_transaction(data)
    flash('İşlem kaydedildi.', 'success')
    return redirect(url_for('erp.index', tab='transactions'))


@bp.route('/settings', methods=['POST'])
def update_settings():
    data = {
        'erp_mode': request.form.get('erp_mode', 'builtin'),
        'external_erp_url': request.form.get('external_erp_url'),
        'external_erp_api_key': request.form.get('external_erp_api_key'),
        'external_erp_type': request.form.get('external_erp_type'),
    }
    finance_model.update_erp_settings(data)
    flash('ERP ayarları güncellendi.', 'success')
    return redirect(url_for('erp.index', tab='settings'))
