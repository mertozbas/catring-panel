from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import purchase as purchase_model
from models import recipe as recipe_model

bp = Blueprint('dietitian', __name__)


@bp.route('/')
def index():
    tab = request.args.get('tab', 'inspection')
    pending = purchase_model.get_all_purchases()
    pending = [p for p in pending if p['status'] in ('received', 'pending')]
    recipes = recipe_model.get_all_recipes()
    return render_template('dietitian.html',
                           pending_purchases=pending, recipes=recipes, tab=tab)


@bp.route('/inspect/<int:purchase_id>')
def inspect(purchase_id):
    purchase = purchase_model.get_purchase(purchase_id)
    items = purchase_model.get_purchase_items(purchase_id)
    return render_template('dietitian_inspect.html', purchase=purchase, items=items)


@bp.route('/inspect/<int:purchase_id>/item/<int:item_id>', methods=['POST'])
def inspect_item(purchase_id, item_id):
    accepted = request.form.get('accepted') == '1'
    reason = request.form.get('rejection_reason', '')
    purchase_model.inspect_purchase_item(item_id, accepted, reason)
    flash('Kalem kontrol edildi.', 'success')
    return redirect(url_for('dietitian.inspect', purchase_id=purchase_id))


@bp.route('/inspect/<int:purchase_id>/complete', methods=['POST'])
def complete_inspection(purchase_id):
    # Tüm kalemlerin kontrol edilip edilmediğini doğrula
    items = purchase_model.get_purchase_items(purchase_id)
    unreviewed = [i for i in items if i['is_accepted'] is None]
    if unreviewed:
        flash(f'{len(unreviewed)} kalem henüz kontrol edilmedi. Önce tüm kalemleri kontrol edin.', 'warning')
        return redirect(url_for('dietitian.inspect', purchase_id=purchase_id))

    inspected_by = request.form.get('inspected_by', 'Diyetisyen')
    notes = request.form.get('notes', '')
    purchase_model.inspect_purchase(purchase_id, inspected_by, notes)

    # OTOMATİK: Kabul edilen kalemleri stoka ekle
    from models import inventory as inv_model
    added = inv_model.add_stock_from_purchase(purchase_id)

    # OTOMATİK: ERP'ye gider kaydı oluştur - sadece kabul edilen kalemlerin tutarı
    purchase = purchase_model.get_purchase(purchase_id)
    accepted_total = sum(i['total_price'] or 0 for i in items if i['is_accepted'] == 1)
    if accepted_total > 0:
        from models import finance as finance_model
        finance_model.create_transaction({
            'type': 'expense',
            'category': 'malzeme',
            'description': f"Satınalma #{purchase_id} - {purchase['supplier_name']}",
            'amount': accepted_total,
            'date': purchase['date'],
            'purchase_id': purchase_id,
        })

    flash(f'Kontrol tamamlandı. {added} kalem stoka eklendi.', 'success')
    return redirect(url_for('dietitian.index'))


@bp.route('/recipes')
def recipes():
    recipes = recipe_model.get_all_recipes()
    return render_template('dietitian.html', recipes=recipes, tab='recipes', pending_purchases=[])


@bp.route('/recipes/add', methods=['POST'])
def add_recipe():
    data = {
        'menu_item_name': request.form.get('menu_item_name'),
        'per_person_cost': request.form.get('per_person_cost') or None,
        'instructions': request.form.get('instructions'),
    }
    recipe_model.create_recipe(data)
    flash('Tarif eklendi.', 'success')
    return redirect(url_for('dietitian.index', tab='recipes'))


@bp.route('/recipes/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = recipe_model.get_recipe(recipe_id)
    ingredients = recipe_model.get_recipe_ingredients(recipe_id)
    return render_template('dietitian_recipe.html', recipe=recipe, ingredients=ingredients)


@bp.route('/recipes/<int:recipe_id>/add-ingredient', methods=['POST'])
def add_ingredient(recipe_id):
    ingredients = recipe_model.get_recipe_ingredients(recipe_id)
    new_list = [{'ingredient_name': i['ingredient_name'],
                 'quantity_per_person': i['quantity_per_person'],
                 'unit': i['unit']} for i in ingredients]
    new_list.append({
        'ingredient_name': request.form.get('ingredient_name'),
        'quantity_per_person': float(request.form.get('quantity_per_person', 0)),
        'unit': request.form.get('unit'),
    })
    recipe_model.save_recipe_ingredients(recipe_id, new_list)
    flash('Malzeme eklendi.', 'success')
    return redirect(url_for('dietitian.recipe_detail', recipe_id=recipe_id))
