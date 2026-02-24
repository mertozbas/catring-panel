from models.db import query_db, insert_db, update_db, get_db


def get_all_recipes():
    return query_db('SELECT * FROM recipes ORDER BY menu_item_name')


def get_recipe(recipe_id):
    return query_db('SELECT * FROM recipes WHERE id = ?', [recipe_id], one=True)


def get_recipe_by_name(name):
    return query_db('SELECT * FROM recipes WHERE menu_item_name = ?', [name], one=True)


def create_recipe(data):
    return insert_db(
        'INSERT INTO recipes (menu_item_name, per_person_cost, instructions) VALUES (?, ?, ?)',
        [data.get('menu_item_name'), data.get('per_person_cost'), data.get('instructions')]
    )


def update_recipe(recipe_id, data):
    return update_db(
        'UPDATE recipes SET menu_item_name=?, per_person_cost=?, instructions=? WHERE id=?',
        [data.get('menu_item_name'), data.get('per_person_cost'),
         data.get('instructions'), recipe_id]
    )


def get_recipe_ingredients(recipe_id):
    return query_db(
        'SELECT * FROM recipe_ingredients WHERE recipe_id = ? ORDER BY ingredient_name',
        [recipe_id]
    )


def save_recipe_ingredients(recipe_id, ingredients):
    db = get_db()
    db.execute('DELETE FROM recipe_ingredients WHERE recipe_id = ?', [recipe_id])
    for ing in ingredients:
        db.execute(
            'INSERT INTO recipe_ingredients (recipe_id, ingredient_name, quantity_per_person, unit) VALUES (?, ?, ?, ?)',
            [recipe_id, ing['ingredient_name'], ing['quantity_per_person'], ing['unit']]
        )
    db.commit()


def delete_recipe(recipe_id):
    db = get_db()
    db.execute('DELETE FROM recipe_ingredients WHERE recipe_id = ?', [recipe_id])
    db.execute('DELETE FROM recipes WHERE id = ?', [recipe_id])
    db.commit()
