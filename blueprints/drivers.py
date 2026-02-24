from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import driver as driver_model

bp = Blueprint('drivers', __name__)


@bp.route('/')
def index():
    drivers = driver_model.get_all_drivers(active_only=False)
    return render_template('drivers.html', drivers=drivers)


@bp.route('/add', methods=['POST'])
def add():
    data = {
        'name': request.form.get('name'),
        'phone': request.form.get('phone'),
        'telegram_chat_id': request.form.get('telegram_chat_id'),
    }
    driver_model.create_driver(data)
    flash('Şoför başarıyla eklendi.', 'success')
    return redirect(url_for('drivers.index'))


@bp.route('/edit/<int:driver_id>', methods=['POST'])
def edit(driver_id):
    data = {
        'name': request.form.get('name'),
        'phone': request.form.get('phone'),
        'telegram_chat_id': request.form.get('telegram_chat_id'),
    }
    driver_model.update_driver(driver_id, data)
    flash('Şoför güncellendi.', 'success')
    return redirect(url_for('drivers.index'))


@bp.route('/toggle/<int:driver_id>/<int:active>')
def toggle(driver_id, active):
    driver_model.toggle_driver(driver_id, active)
    flash('Şoför durumu güncellendi.', 'success')
    return redirect(url_for('drivers.index'))
