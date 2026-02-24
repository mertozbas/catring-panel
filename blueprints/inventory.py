from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import inventory as inv_model

bp = Blueprint('inventory', __name__)


@bp.route('/')
def index():
    items = inv_model.get_all_inventory()
    low_stock = inv_model.get_low_stock_items()
    return render_template('inventory.html', items=items, low_stock=low_stock)


@bp.route('/add', methods=['POST'])
def add():
    data = {
        'ingredient_name': request.form.get('ingredient_name'),
        'current_stock': float(request.form.get('current_stock', 0)),
        'unit': request.form.get('unit'),
        'min_stock_level': float(request.form.get('min_stock_level', 0)),
    }
    inv_model.create_inventory_item(data)
    flash('Malzeme eklendi.', 'success')
    return redirect(url_for('inventory.index'))


@bp.route('/edit/<int:item_id>', methods=['POST'])
def edit(item_id):
    data = {
        'ingredient_name': request.form.get('ingredient_name'),
        'current_stock': float(request.form.get('current_stock', 0)),
        'unit': request.form.get('unit'),
        'min_stock_level': float(request.form.get('min_stock_level', 0)),
    }
    inv_model.update_inventory_item(item_id, data)
    flash('Malzeme güncellendi.', 'success')
    return redirect(url_for('inventory.index'))


@bp.route('/adjust/<int:item_id>', methods=['POST'])
def adjust(item_id):
    change = float(request.form.get('quantity_change', 0))
    inv_model.update_stock(item_id, change)
    flash('Stok güncellendi.', 'success')
    return redirect(url_for('inventory.index'))


@bp.route('/delete/<int:item_id>')
def delete(item_id):
    inv_model.delete_inventory_item(item_id)
    flash('Malzeme silindi.', 'success')
    return redirect(url_for('inventory.index'))
