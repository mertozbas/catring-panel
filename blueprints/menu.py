from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models import menu as menu_model
import json
import io

bp = Blueprint('menu', __name__)

DAY_NAMES = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi']
CATEGORIES = ['corba', 'ana_yemek', 'garnitur', 'tatli']


@bp.route('/')
def index():
    menus = menu_model.get_all_menus()
    return render_template('menu.html', menus=menus, day_names=DAY_NAMES)


@bp.route('/create', methods=['POST'])
def create():
    week_start = request.form.get('week_start_date')
    existing = menu_model.get_menu_by_week(week_start)
    if existing:
        flash('Bu hafta için zaten bir menü var.', 'warning')
        return redirect(url_for('menu.edit', menu_id=existing['id']))
    menu_id = menu_model.create_menu(week_start)
    flash('Menü oluşturuldu. Şimdi yemekleri ekleyin.', 'success')
    return redirect(url_for('menu.edit', menu_id=menu_id))


@bp.route('/edit/<int:menu_id>')
def edit(menu_id):
    menu = menu_model.get_menu(menu_id)
    items = menu_model.get_menu_items(menu_id)

    menu_data = {}
    for day in range(6):
        menu_data[day] = {}
        for order in range(1, 5):
            menu_data[day][order] = ''

    for item in items:
        menu_data[item['day_of_week']][item['item_order']] = item['item_name']

    return render_template('menu_edit.html', menu=menu, menu_data=menu_data,
                           day_names=DAY_NAMES, categories=CATEGORIES)


@bp.route('/save/<int:menu_id>', methods=['POST'])
def save(menu_id):
    items = []
    for day in range(6):
        for order in range(1, 5):
            name = request.form.get(f'item_{day}_{order}', '').strip()
            if name:
                cat = CATEGORIES[order - 1] if order <= len(CATEGORIES) else None
                items.append({
                    'day_of_week': day,
                    'item_order': order,
                    'item_name': name,
                    'category': cat
                })
    menu_model.save_menu_items(menu_id, items)
    flash('Menü kaydedildi.', 'success')
    return redirect(url_for('menu.edit', menu_id=menu_id))


@bp.route('/publish/<int:menu_id>')
def publish(menu_id):
    menu_model.update_menu_status(menu_id, 'published')
    flash('Menü yayınlandı.', 'success')
    return redirect(url_for('menu.index'))


@bp.route('/delete/<int:menu_id>')
def delete(menu_id):
    menu_model.delete_menu(menu_id)
    flash('Menü silindi.', 'success')
    return redirect(url_for('menu.index'))


@bp.route('/print/<int:menu_id>')
def print_menu(menu_id):
    menu = menu_model.get_menu(menu_id)
    items = menu_model.get_menu_items(menu_id)

    menu_data = {}
    for day in range(6):
        menu_data[day] = []
    for item in items:
        menu_data[item['day_of_week']].append(item['item_name'])

    return render_template('menu_print.html', menu=menu, menu_data=menu_data, day_names=DAY_NAMES)


@bp.route('/pdf/<int:menu_id>')
def pdf(menu_id):
    from utils.pdf_generator import generate_menu_pdf
    menu = menu_model.get_menu(menu_id)
    items = menu_model.get_menu_items(menu_id)

    menu_data = {}
    for day in range(6):
        menu_data[day] = []
    for item in items:
        menu_data[item['day_of_week']].append(item['item_name'])

    pdf_buffer = generate_menu_pdf(menu, menu_data, DAY_NAMES)
    return send_file(pdf_buffer, mimetype='application/pdf',
                     download_name=f'menu_{menu["week_start_date"]}.pdf')
