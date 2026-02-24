from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import query_db
from models import order as order_model
from models import menu as menu_model
from models import recipe as recipe_model
from models import inventory as inv_model
from datetime import date

bp = Blueprint('kitchen', __name__)


@bp.route('/')
def index():
    selected_date = request.args.get('date', date.today().isoformat())

    summary = order_model.get_daily_summary(selected_date)

    orders = order_model.get_orders_by_date(selected_date)

    container_summary = query_db(
        '''SELECT container_type, COUNT(*) as order_count, SUM(portion_count) as total_portions
           FROM orders WHERE date=?
           GROUP BY container_type''', [selected_date])

    route_summary = query_db(
        '''SELECT r.route_name, r.id as route_id,
                  COUNT(o.id) as order_count, SUM(o.portion_count) as total_portions,
                  r.optimized_duration_min as estimated_duration
           FROM routes r
           LEFT JOIN orders o ON o.route_id = r.id AND o.date = r.date
           WHERE r.date = ?
           GROUP BY r.id
           ORDER BY r.route_name''', [selected_date])

    current_menu = menu_model.get_current_week_menu()
    menu_items = []
    prep_list = []
    if current_menu:
        day_of_week = date.fromisoformat(selected_date).weekday()
        if day_of_week < 6:
            menu_items = query_db(
                'SELECT * FROM menu_items WHERE weekly_menu_id=? AND day_of_week=? ORDER BY item_order',
                [current_menu['id'], day_of_week])

            # Hazırlık listesi: her menü kalemi için tarif ve malzeme bilgisi
            total_portions = summary['total_portions'] or 0
            for mi in menu_items:
                recipe = recipe_model.get_recipe_by_name(mi['item_name'])
                ingredients = []
                if recipe:
                    raw_ings = recipe_model.get_recipe_ingredients(recipe['id'])
                    for ing in raw_ings:
                        needed = round(ing['quantity_per_person'] * total_portions, 2)
                        inv = inv_model.get_inventory_by_name(ing['ingredient_name'])
                        stock = inv['current_stock'] if inv else 0
                        ingredients.append({
                            'name': ing['ingredient_name'],
                            'needed': needed,
                            'unit': ing['unit'],
                            'stock': stock,
                            'enough': stock >= needed,
                        })
                prep_list.append({
                    'item_name': mi['item_name'],
                    'category': mi['category'],
                    'recipe': recipe,
                    'ingredients': ingredients,
                    'total_portions': total_portions,
                })

    # Durum özeti
    status_counts = {
        'pending': len([o for o in orders if o['status'] == 'pending']),
        'preparing': len([o for o in orders if o['status'] == 'preparing']),
        'ready': len([o for o in orders if o['status'] == 'ready']),
        'delivering': len([o for o in orders if o['status'] == 'delivering']),
        'delivered': len([o for o in orders if o['status'] == 'delivered']),
    }

    return render_template('kitchen.html',
                           selected_date=selected_date,
                           summary=summary,
                           orders=orders,
                           container_summary=container_summary,
                           route_summary=route_summary,
                           menu_items=menu_items,
                           prep_list=prep_list,
                           status_counts=status_counts)


@bp.route('/start-preparing', methods=['POST'])
def start_preparing():
    """Tüm pending siparişleri 'preparing' durumuna geçir."""
    selected_date = request.form.get('date', date.today().isoformat())
    count = order_model.bulk_update_status(selected_date, 'pending', 'preparing')
    flash(f'{count} sipariş hazırlanıyor durumuna geçirildi.', 'success')
    return redirect(url_for('kitchen.index', date=selected_date))


@bp.route('/mark-ready', methods=['POST'])
def mark_ready():
    """Tüm preparing siparişleri 'ready' durumuna geçir."""
    selected_date = request.form.get('date', date.today().isoformat())
    count = order_model.bulk_update_status(selected_date, 'preparing', 'ready')

    # OTOMATİK: Stoktan malzeme düş
    summary = order_model.get_daily_summary(selected_date)
    total_portions = summary['total_portions'] or 0
    if total_portions > 0:
        deducted = inv_model.deduct_stock_for_production(selected_date, total_portions)

    flash(f'{count} sipariş hazır durumuna geçirildi. Stoklar güncellendi.', 'success')
    return redirect(url_for('kitchen.index', date=selected_date))
