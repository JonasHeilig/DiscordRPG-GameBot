from flask import Blueprint, request, jsonify, session
from functools import wraps
from bot.database.db_manager import DatabaseManager

api_bp = Blueprint('api', __name__, url_prefix='/api')
db = DatabaseManager()


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"\Session Keys: {list(session.keys())}")
        print(f"Gamemaster: {session.get('gamemaster')}")
        print(f"Server ID: {session.get('server_id')}")

        if 'gamemaster' not in session:
            print(f"AUTH FAILED")
            return jsonify({'error': 'Not Authenticated'}), 401

        print(f"AUTH SUCCESS")
        return f(*args, **kwargs)

    return decorated_function


@api_bp.route('/servers', methods=['GET'])
@auth_required
def get_servers():
    servers = db.get_all_servers()
    return jsonify(servers)


@api_bp.route('/server/<int:server_id>/users', methods=['GET'])
@auth_required
def get_server_users(server_id):
    if session.get('server_id') != server_id:
        print(f"Server ID not matching")
        return jsonify({'error': 'Missing Right'}), 403

    users = db.get_server_users(server_id)
    print(f"GET USERS {len(users)} Player not found")
    return jsonify(users)


@api_bp.route('/server/<int:server_id>/user/<int:user_id>/ore', methods=['POST'])
@auth_required
def add_ore(server_id, user_id):
    if session.get('server_id') != server_id:
        return jsonify({'error': 'Missing Right'}), 403

    data = request.get_json()
    ore_type = data.get('ore_type')
    amount = data.get('amount', 1)

    print(f"ADD ORE User: {user_id}, Ore: {ore_type}, Amount: {amount}")

    if not ore_type or not isinstance(amount, int) or amount < 0:
        return jsonify({'error': 'Invalid Request'}), 400

    if db.add_ore(user_id, server_id, ore_type, amount):
        print(f"Ore added successfully")
        return jsonify({'success': True})

    print(f"Error by adding ore")
    return jsonify({'error': 'Error by adding'}), 500


@api_bp.route('/server/<int:server_id>/ore-probability', methods=['POST'])
@auth_required
def update_ore_probability(server_id):
    session_server_id = session.get('server_id')

    try:
        session_server_int = int(session_server_id) if session_server_id else None
        if session_server_int != server_id:
            return jsonify({'error': 'Missing Rights'}), 403
    except (ValueError, TypeError):
        return jsonify({'error': 'Missing Rights'}), 403

    data = request.get_json()
    ore_type = data.get('ore_type')
    probability = data.get('probability')

    print(f"Update Ore: {ore_type}, Probability: {probability}")

    if not ore_type or not isinstance(probability, (int, float)):
        return jsonify({'error': 'Invalid Request'}), 400

    if 0 <= probability <= 100:
        if db.update_ore_probability(server_id, ore_type, probability):
            print(f"Updated Successfully: {ore_type} = {probability}%")
            return jsonify({'success': True})

    print(f"Probability out of range: {probability}")
    return jsonify({'error': 'Invalid Probability (0-100)'}), 400


@api_bp.route('/server/<int:server_id>/probabilities', methods=['GET'])
@auth_required
def get_probabilities(server_id):
    if session.get('server_id') != server_id:
        return jsonify({'error': 'Missing Rights'}), 403

    probs = db.get_ore_probabilities(server_id)
    return jsonify(probs)
