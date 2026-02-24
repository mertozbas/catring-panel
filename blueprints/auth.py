from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from models import user as user_model

bp = Blueprint('auth', __name__)

# Rol -> erişebileceği blueprint listesi
ROLE_PERMISSIONS = {
    'admin': '__all__',
    'siparis': ['dashboard', 'orders', 'customers'],
    'mutfak': ['dashboard', 'kitchen', 'menu', 'inventory'],
    'diyetisyen': ['dashboard', 'dietitian', 'menu', 'inventory'],
    'sofor': ['driver_ui'],
    'planlama': ['dashboard', 'planning', 'purchasing', 'inventory'],
    'muhasebe': ['dashboard', 'erp'],
}

ROLE_LABELS = {
    'admin': 'Yönetici',
    'siparis': 'Sipariş',
    'mutfak': 'Mutfak',
    'diyetisyen': 'Diyetisyen',
    'sofor': 'Şoför',
    'planlama': 'Planlama',
    'muhasebe': 'Muhasebe',
}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Lütfen giriş yapın.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_allowed_blueprints(role):
    perms = ROLE_PERMISSIONS.get(role, [])
    return perms


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        role = session.get('user_role', '')
        if role == 'sofor':
            return redirect(url_for('driver_ui.index'))
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = user_model.get_user_by_username(username)
        if user and user_model.verify_password(user, password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_role'] = user['role']
            session['username'] = user['username']
            session['driver_id'] = user['driver_id'] if 'driver_id' in user.keys() else None
            flash(f'Hoşgeldiniz, {user["full_name"]}!', 'success')

            if user['role'] == 'sofor':
                return redirect(url_for('driver_ui.index'))
            return redirect(url_for('dashboard.index'))

        flash('Kullanıcı adı veya şifre hatalı.', 'danger')

    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('Çıkış yapıldı.', 'success')
    return redirect(url_for('auth.login'))
