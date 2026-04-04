from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps
from bot.database.db_manager import DatabaseManager

dashboard_bp = Blueprint('dashboard', __name__)
db = DatabaseManager()


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'gamemaster' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


@dashboard_bp.route('/')
def index():
    if 'gamemaster' not in session:
        return redirect(url_for('auth.login'))

    servers = db.get_all_servers()

    return render_template('dashboard.html', servers=servers)


@dashboard_bp.route('/server/<int:server_id>')
def server_details(server_id):
    if 'gamemaster' not in session:
        return redirect(url_for('auth.login'))

    if session.get('server_id') != server_id:
        return "Missing Rights", 403

    server_info = db.get_server_info(server_id)
    users = db.get_server_users(server_id)
    probabilities = db.get_ore_probabilities(server_id)

    if not server_info:
        return "Server not found", 404

    return render_template('server_details.html',
                           server=server_info,
                           users=users,
                           probabilities=probabilities)


@dashboard_bp.route('/server/<int:server_id>/users')
def user_management(server_id):
    if 'gamemaster' not in session:
        return redirect(url_for('auth.login'))

    if session.get('server_id') != server_id:
        return "Missing Rights", 403

    users = db.get_server_users(server_id)

    return render_template('user_management.html',
                           server_id=server_id,
                           users=users)