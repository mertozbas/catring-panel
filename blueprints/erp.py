from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models import finance as finance_model
from models import customer as customer_model
from datetime import date, timedelta
from utils.pdf_generator import generate_invoice_pdf

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

    # Cari hesap verileri
    customer_balances = finance_model.get_all_customer_balances()
    recent_payments = finance_model.get_all_payments(20)

    # Gider kırılımı
    expense_breakdown = finance_model.get_period_expense_breakdown(month_start, month_end)

    # Dönem karşılaştırması (bu ay vs geçen ay)
    prev_month_end = (today.replace(day=1) - timedelta(days=1))
    prev_month_start = prev_month_end.replace(day=1)
    comparison = finance_model.get_period_comparison(
        month_start, month_end,
        prev_month_start.isoformat(), prev_month_end.isoformat()
    )

    # Aylık trend (convert Row to dict for JSON serialization)
    monthly_trend_raw = finance_model.get_monthly_trend(6)
    monthly_trend = [dict(row) for row in monthly_trend_raw] if monthly_trend_raw else []

    # Gider kırılımı - convert to dict for JSON
    expense_breakdown = [dict(row) for row in expense_breakdown] if expense_breakdown else []

    # Ödenmemiş faturalar
    unpaid_invoices = finance_model.get_unpaid_invoices()

    return render_template('erp.html',
                           tab=tab,
                           summary=summary,
                           recent_transactions=recent_transactions,
                           invoices=invoices,
                           customers=customers,
                           erp_settings=erp_settings,
                           month_start=month_start,
                           month_end=month_end,
                           customer_balances=customer_balances,
                           recent_payments=recent_payments,
                           expense_breakdown=expense_breakdown,
                           comparison=comparison,
                           monthly_trend=monthly_trend,
                           unpaid_invoices=unpaid_invoices)


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


@bp.route('/invoices/auto-generate', methods=['POST'])
def auto_generate_invoice():
    """Otomatik fatura oluştur - dönem + müşteri seçimi."""
    customer_id = request.form.get('customer_id')
    period_start = request.form.get('period_start')
    period_end = request.form.get('period_end')
    unit_price = float(request.form.get('unit_price', 0) or 0)
    tax_rate = float(request.form.get('tax_rate', 10) or 10)

    if not customer_id or not period_start or not period_end:
        flash('Müşteri ve dönem bilgileri gerekli.', 'danger')
        return redirect(url_for('erp.index', tab='invoices'))

    # Müşterinin birim fiyatını kullan (form'dan gelmediyse)
    if unit_price == 0:
        cust = customer_model.get_customer(int(customer_id))
        if cust and cust['unit_price']:
            unit_price = cust['unit_price']

    if unit_price == 0:
        flash('Birim fiyat belirtilmedi ve müşterinin varsayılan birim fiyatı yok.', 'danger')
        return redirect(url_for('erp.index', tab='invoices'))

    invoice_id = finance_model.generate_auto_invoice(
        int(customer_id), period_start, period_end, unit_price, tax_rate
    )

    if invoice_id:
        flash('Otomatik fatura oluşturuldu.', 'success')
    else:
        flash('Bu dönemde müşterinin siparişi bulunamadı.', 'warning')
    return redirect(url_for('erp.index', tab='invoices'))


@bp.route('/invoices/<int:invoice_id>/status/<status>')
def update_invoice_status(invoice_id, status):
    finance_model.update_invoice_status(invoice_id, status)
    flash('Fatura durumu güncellendi.', 'success')
    return redirect(url_for('erp.index', tab='invoices'))


@bp.route('/invoices/<int:invoice_id>/pdf')
def invoice_pdf(invoice_id):
    """Fatura PDF'i oluştur ve indir."""
    invoice = finance_model.get_invoice(invoice_id)
    if not invoice:
        flash('Fatura bulunamadı.', 'danger')
        return redirect(url_for('erp.index', tab='invoices'))

    buffer = generate_invoice_pdf(dict(invoice))
    filename = f"fatura_{invoice['invoice_number']}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')


@bp.route('/invoices/calculate-portions', methods=['POST'])
def calculate_portions():
    """AJAX: Dönem porsiyon hesapla."""
    import json
    customer_id = request.form.get('customer_id')
    period_start = request.form.get('period_start')
    period_end = request.form.get('period_end')

    if not all([customer_id, period_start, period_end]):
        return json.dumps({'error': 'Eksik parametre'}), 400

    result = finance_model.calculate_customer_portions(
        int(customer_id), period_start, period_end
    )
    cust = customer_model.get_customer(int(customer_id))
    unit_price = cust['unit_price'] if cust and cust['unit_price'] else 0

    return json.dumps({
        'total_portions': result['total_portions'] or 0,
        'order_count': result['order_count'] or 0,
        'unit_price': unit_price,
    }), 200, {'Content-Type': 'application/json'}


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


@bp.route('/payments/add', methods=['POST'])
def add_payment():
    """Ödeme kaydı ekle."""
    data = {
        'customer_id': request.form.get('customer_id'),
        'invoice_id': request.form.get('invoice_id') or None,
        'amount': float(request.form.get('amount', 0)),
        'date': request.form.get('date'),
        'payment_method': request.form.get('payment_method', 'nakit'),
        'notes': request.form.get('notes'),
    }
    finance_model.create_payment(data)

    # Faturaya bağlı ödeme yapıldıysa, fatura durumunu kontrol et
    if data['invoice_id']:
        inv = finance_model.get_invoice(int(data['invoice_id']))
        if inv:
            balance = finance_model.get_customer_balance(int(data['customer_id']))
            # Basit kontrol: toplam ödeme >= toplam borç ise ödendi say
            if balance and balance['total_paid'] >= balance['total_debt']:
                finance_model.update_invoice_status(int(data['invoice_id']), 'paid')

    flash('Ödeme kaydedildi.', 'success')
    return redirect(url_for('erp.index', tab='cari'))


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
