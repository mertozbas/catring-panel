from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import purchase as purchase_model
from models import supplier as supplier_model

bp = Blueprint('purchasing', __name__)


@bp.route('/')
def index():
    tab = request.args.get('tab', 'purchases')
    purchases = purchase_model.get_all_purchases()
    suppliers = supplier_model.get_all_suppliers(active_only=False)
    return render_template('purchasing.html',
                           purchases=purchases, suppliers=suppliers, tab=tab)


@bp.route('/suppliers/add', methods=['POST'])
def add_supplier():
    data = {
        'name': request.form.get('name'),
        'contact_name': request.form.get('contact_name'),
        'phone': request.form.get('phone'),
        'address': request.form.get('address'),
        'category': request.form.get('category'),
    }
    supplier_model.create_supplier(data)
    flash('Tedarikçi eklendi.', 'success')
    return redirect(url_for('purchasing.index', tab='suppliers'))


@bp.route('/suppliers/edit/<int:supplier_id>', methods=['POST'])
def edit_supplier(supplier_id):
    data = {
        'name': request.form.get('name'),
        'contact_name': request.form.get('contact_name'),
        'phone': request.form.get('phone'),
        'address': request.form.get('address'),
        'category': request.form.get('category'),
    }
    supplier_model.update_supplier(supplier_id, data)
    flash('Tedarikçi güncellendi.', 'success')
    return redirect(url_for('purchasing.index', tab='suppliers'))


@bp.route('/add', methods=['POST'])
def add():
    data = {
        'supplier_id': request.form.get('supplier_id'),
        'date': request.form.get('date'),
        'total_amount': request.form.get('total_amount', 0),
    }
    purchase_id = purchase_model.create_purchase(data)
    flash('Satınalma kaydı oluşturuldu.', 'success')
    return redirect(url_for('purchasing.detail', purchase_id=purchase_id))


@bp.route('/detail/<int:purchase_id>')
def detail(purchase_id):
    purchase = purchase_model.get_purchase(purchase_id)
    items = purchase_model.get_purchase_items(purchase_id)
    return render_template('purchasing_detail.html', purchase=purchase, items=items)


@bp.route('/detail/<int:purchase_id>/add-item', methods=['POST'])
def add_item(purchase_id):
    data = {
        'purchase_id': purchase_id,
        'ingredient_name': request.form.get('ingredient_name'),
        'quantity': float(request.form.get('quantity', 0)),
        'unit': request.form.get('unit'),
        'unit_price': float(request.form.get('unit_price', 0)),
        'total_price': float(request.form.get('quantity', 0)) * float(request.form.get('unit_price', 0)),
    }
    purchase_model.add_purchase_item(data)
    flash('Kalem eklendi.', 'success')
    return redirect(url_for('purchasing.detail', purchase_id=purchase_id))


@bp.route('/receive/<int:purchase_id>', methods=['POST'])
def receive(purchase_id):
    """Satınalmayı teslim alındı olarak işaretle."""
    purchase_model.update_purchase_status(purchase_id, 'received')
    flash('Satınalma teslim alındı olarak işaretlendi. Diyetisyen kontrolüne gönderildi.', 'success')
    return redirect(url_for('purchasing.detail', purchase_id=purchase_id))
