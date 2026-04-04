from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from bot.database.db_manager import DatabaseManager

auth_bp = Blueprint('auth', __name__, url_prefix='')
db = DatabaseManager()


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'gamemaster' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token = request.form.get('token', '').strip()

        if not token:
            return render_template('login.html', error='Token required'), 403

        result = db.verify_token(token)
        if not result:
            return render_template('login.html', error='Invalid token'), 403

        session['gamemaster'] = result['gamemaster_id']
        session['server_id'] = result['server_id']

        return redirect(url_for('dashboard.index'))

    return render_template('login.html', error=None)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))