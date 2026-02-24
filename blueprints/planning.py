from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import query_db
from models import menu as menu_model
from models import recipe as recipe_model

bp = Blueprint('planning', __name__)


@bp.route('/')
def index():
    menu_id = request.args.get('menu_id')
    menus = menu_model.get_all_menus()

    planning_data = []
    selected_menu = None
    total_portions = 0

    if menu_id:
        selected_menu = menu_model.get_menu(int(menu_id))
        items = menu_model.get_menu_items(int(menu_id))

        if selected_menu:
            avg_daily = query_db(
                '''SELECT COALESCE(AVG(daily_total), 0) as avg_portions FROM (
                     SELECT date, SUM(portion_count) as daily_total
                     FROM orders
                     GROUP BY date
                     ORDER BY date DESC LIMIT 5
                   )''', one=True)
            total_portions = int(avg_daily['avg_portions']) if avg_daily else 1000

        ingredient_totals = {}
        for item in items:
            recipe = recipe_model.get_recipe_by_name(item['item_name'])
            if recipe:
                ingredients = recipe_model.get_recipe_ingredients(recipe['id'])
                for ing in ingredients:
                    key = (ing['ingredient_name'], ing['unit'])
                    needed = ing['quantity_per_person'] * total_portions
                    if key in ingredient_totals:
                        ingredient_totals[key] += needed
                    else:
                        ingredient_totals[key] = needed

        for (name, unit), total in sorted(ingredient_totals.items()):
            stock = query_db(
                'SELECT current_stock FROM inventory WHERE ingredient_name = ?',
                [name], one=True)
            current = stock['current_stock'] if stock else 0
            planning_data.append({
                'ingredient_name': name,
                'unit': unit,
                'needed': round(total, 2),
                'current_stock': current,
                'to_buy': round(max(0, total - current), 2)
            })

    return render_template('planning.html',
                           menus=menus,
                           selected_menu=selected_menu,
                           planning_data=planning_data,
                           total_portions=total_portions,
                           menu_id=menu_id)


@bp.route('/generate-purchase', methods=['POST'])
def generate_purchase():
    """Planlama verilerinden satınalma siparişi oluştur."""
    menu_id = request.form.get('menu_id')
    if not menu_id:
        flash('Menü seçilmedi.', 'warning')
        return redirect(url_for('planning.index'))

    from models import purchase as purchase_model
    from models import supplier as supplier_model
    from models import inventory as inv_model
    from datetime import date as dt

    selected_menu = menu_model.get_menu(int(menu_id))
    items = menu_model.get_menu_items(int(menu_id))

    avg_daily = query_db(
        '''SELECT COALESCE(AVG(daily_total), 0) as avg_portions FROM (
             SELECT date, SUM(portion_count) as daily_total
             FROM orders GROUP BY date ORDER BY date DESC LIMIT 5
           )''', one=True)
    total_portions = int(avg_daily['avg_portions']) if avg_daily else 1000

    # Malzeme ihtiyacını hesapla
    to_buy = []
    for item in items:
        recipe = recipe_model.get_recipe_by_name(item['item_name'])
        if recipe:
            ingredients = recipe_model.get_recipe_ingredients(recipe['id'])
            for ing in ingredients:
                needed = ing['quantity_per_person'] * total_portions
                inv = inv_model.get_inventory_by_name(ing['ingredient_name'])
                current = inv['current_stock'] if inv else 0
                deficit = max(0, needed - current)
                if deficit > 0:
                    to_buy.append({
                        'ingredient_name': ing['ingredient_name'],
                        'quantity': round(deficit, 2),
                        'unit': ing['unit'],
                    })

    if not to_buy:
        flash('Satın alınacak malzeme yok, stok yeterli.', 'info')
        return redirect(url_for('planning.index', menu_id=menu_id))

    # İlk aktif tedarikçiyi bul (veya varsayılan oluştur)
    suppliers = supplier_model.get_all_suppliers(active_only=True)
    supplier_id = suppliers[0]['id'] if suppliers else 1

    # Satınalma oluştur
    purchase_id = purchase_model.create_purchase({
        'supplier_id': supplier_id,
        'date': dt.today().isoformat(),
        'total_amount': 0,
        'status': 'pending',
    })

    # Kalemleri ekle
    purchase_model.save_purchase_items(purchase_id, to_buy)

    flash(f'Satınalma siparişi oluşturuldu ({len(to_buy)} kalem).', 'success')
    return redirect(url_for('purchasing.detail', purchase_id=purchase_id))
