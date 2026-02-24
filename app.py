from flask import Flask, redirect, url_for, session, request
import config
from models.db import init_db, close_db


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DATABASE_PATH'] = config.DATABASE_PATH

    init_db(app)
    app.teardown_appcontext(close_db)

    from blueprints.auth import bp as auth_bp
    from blueprints.dashboard import bp as dashboard_bp
    from blueprints.customers import bp as customers_bp
    from blueprints.drivers import bp as drivers_bp
    from blueprints.menu import bp as menu_bp
    from blueprints.orders import bp as orders_bp
    from blueprints.routes import bp as routes_bp
    from blueprints.kitchen import bp as kitchen_bp
    from blueprints.driver_ui import bp as driver_ui_bp
    from blueprints.inventory import bp as inventory_bp
    from blueprints.planning import bp as planning_bp
    from blueprints.purchasing import bp as purchasing_bp
    from blueprints.dietitian import bp as dietitian_bp
    from blueprints.erp import bp as erp_bp
    from blueprints.api import bp as api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(drivers_bp, url_prefix='/drivers')
    app.register_blueprint(menu_bp, url_prefix='/menu')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(routes_bp, url_prefix='/routes')
    app.register_blueprint(kitchen_bp, url_prefix='/kitchen')
    app.register_blueprint(driver_ui_bp, url_prefix='/driver')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(planning_bp, url_prefix='/planning')
    app.register_blueprint(purchasing_bp, url_prefix='/purchasing')
    app.register_blueprint(dietitian_bp, url_prefix='/dietitian')
    app.register_blueprint(erp_bp, url_prefix='/erp')
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.before_request
    def require_login():
        # Login gerektirmeyen endpoint'ler
        allowed_endpoints = ['auth.login', 'auth.logout', 'static', 'service_worker']
        if request.endpoint and (
            request.endpoint in allowed_endpoints
            or request.endpoint.startswith('api.')
        ):
            return

        # Giriş yapmamışsa login'e yönlendir
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        # Rol bazlı erişim kontrolü
        from blueprints.auth import ROLE_PERMISSIONS
        role = session.get('user_role', '')
        perms = ROLE_PERMISSIONS.get(role, [])

        if perms != '__all__' and request.blueprint:
            if request.blueprint not in perms and request.blueprint != 'auth':
                from flask import flash
                flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
                if role == 'sofor':
                    return redirect(url_for('driver_ui.index'))
                return redirect(url_for('dashboard.index'))

    @app.context_processor
    def inject_user():
        from blueprints.auth import ROLE_PERMISSIONS, ROLE_LABELS
        user_role = session.get('user_role', '')
        perms = ROLE_PERMISSIONS.get(user_role, [])
        return {
            'current_user': {
                'id': session.get('user_id'),
                'name': session.get('user_name', ''),
                'role': user_role,
                'role_label': ROLE_LABELS.get(user_role, user_role),
                'username': session.get('username', ''),
            },
            'allowed_blueprints': perms,
            'is_logged_in': 'user_id' in session,
        }

    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))

    @app.route('/sw.js')
    def service_worker():
        return app.send_static_file('sw.js'), 200, {
            'Content-Type': 'application/javascript',
            'Service-Worker-Allowed': '/'
        }

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG)
