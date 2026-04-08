from flask import Blueprint, request, jsonify, session
from functools import wraps
from bot.database.db_manager import DatabaseManager
from config import MAX_PLAYER_HEALTH

api_bp = Blueprint('api', __name__, url_prefix='/api')
db = DatabaseManager()


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"Session Keys: {list(session.keys())}")
        print(f"Gamemaster: {session.get('gamemaster')}")
        print(f"Server ID in Session: {session.get('server_id')}")

        if 'gamemaster' not in session:
            print(f"AUTH FAILED - No gamemaster in session")
            return jsonify({'error': 'Not Authenticated', 'code': 'AUTH_FAILED'}), 401

        print(f"AUTH SUCCESS")
        return f(*args, **kwargs)

    return decorated_function


@api_bp.route('/servers', methods=['GET'])
@auth_required
def get_servers():
    try:
        servers = db.get_all_servers()
        return jsonify(servers)
    except Exception as e:
        print(f"Error fetching servers: {e}")
        return jsonify({'error': 'Failed to fetch servers', 'code': 'SERVER_FETCH_ERROR'}), 500


@api_bp.route('/server/<server_id>/users', methods=['GET'])
@auth_required
def get_server_users(server_id):
    session_server_id = session.get('server_id')
    print(f"Comparing: URL server_id={server_id}, Session server_id={session_server_id}")

    if session_server_id is None or str(session_server_id) != str(server_id):
        print(f"Server ID mismatch: {session_server_id} != {server_id}")
        return jsonify({'error': 'Access Denied', 'code': 'PERMISSION_DENIED'}), 403

    try:
        users = db.get_server_users(int(server_id))
        print(f"GET USERS {len(users)} Player found")
        return jsonify(users)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({'error': 'Failed to fetch users', 'code': 'USER_FETCH_ERROR'}), 500


@api_bp.route('/server/<server_id>/user/<user_id>/ore', methods=['POST'])
@auth_required
def add_ore(server_id, user_id):
    session_server_id = session.get('server_id')
    print(f"Add Ore - Comparing: URL server_id={server_id}, Session server_id={session_server_id}")

    if session_server_id is None or str(session_server_id) != str(server_id):
        print(f"Server ID mismatch: {session_server_id} != {server_id}")
        return jsonify({'error': 'Access Denied', 'code': 'PERMISSION_DENIED'}), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request body', 'code': 'INVALID_REQUEST'}), 400

        ore_type = data.get('ore_type')
        amount = data.get('amount', 1)

        print(f"ADD ORE User: {user_id}, Ore: {ore_type}, Amount: {amount}")

        if not ore_type or not isinstance(amount, int) or amount < 0:
            return jsonify({'error': 'Invalid ore type or amount', 'code': 'INVALID_INPUT'}), 400

        if db.add_ore(int(user_id), int(server_id), ore_type, amount):
            print(f"Ore added successfully")
            return jsonify({'success': True, 'message': f'{amount} {ore_type} added'})

        print(f"Error adding ore")
        return jsonify({'error': 'Failed to add ore', 'code': 'ADD_ORE_ERROR'}), 500
    except Exception as e:
        print(f"Error in add_ore: {e}")
        return jsonify({'error': 'Server error', 'code': 'SERVER_ERROR'}), 500


@api_bp.route('/server/<server_id>/user/<user_id>/ore/reduce', methods=['POST'])
@auth_required
def reduce_ore(server_id, user_id):
    session_server_id = session.get('server_id')
    print(f"Reduce Ore - Comparing: URL server_id={server_id}, Session server_id={session_server_id}")

    if session_server_id is None or str(session_server_id) != str(server_id):
        print(f"Server ID mismatch")
        return jsonify({'error': 'Access Denied', 'code': 'PERMISSION_DENIED'}), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request body', 'code': 'INVALID_REQUEST'}), 400

        ore_type = data.get('ore_type')
        amount = data.get('amount', 1)

        print(f"REDUCE ORE User: {user_id}, Ore: {ore_type}, Amount: {amount}")

        if not ore_type or not isinstance(amount, int) or amount < 1:
            return jsonify({'error': 'Invalid ore type or amount', 'code': 'INVALID_INPUT'}), 400

        if db.reduce_ore(int(user_id), int(server_id), ore_type, amount):
            print(f"Ore reduced successfully")
            return jsonify({'success': True, 'message': f'{amount} {ore_type} removed'})

        print(f"Error reducing ore - not enough resources")
        return jsonify({'error': 'Not enough ore', 'code': 'INSUFFICIENT_ORE'}), 400
    except Exception as e:
        print(f"Error in reduce_ore: {e}")
        return jsonify({'error': 'Server error', 'code': 'SERVER_ERROR'}), 500


@api_bp.route('/server/<server_id>/user/<user_id>/health', methods=['POST'])
@auth_required
def update_health(server_id, user_id):
    session_server_id = session.get('server_id')
    print(f"Update Health - Comparing: URL server_id={server_id}, Session server_id={session_server_id}")

    if session_server_id is None or str(session_server_id) != str(server_id):
        print(f"Server ID mismatch")
        return jsonify({'error': 'Access Denied', 'code': 'PERMISSION_DENIED'}), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request body', 'code': 'INVALID_REQUEST'}), 400

        health = data.get('health')

        if health is None or not isinstance(health, int):
            return jsonify({'error': 'Invalid health value', 'code': 'INVALID_INPUT'}), 400

        if health < 0 or health > MAX_PLAYER_HEALTH:
            return jsonify({'error': f'Health must be between 0 and {MAX_PLAYER_HEALTH}', 'code': 'INVALID_RANGE'}), 400

        print(f"UPDATE HEALTH User: {user_id}, Health: {health}")

        if db.update_player_health(int(user_id), int(server_id), health):
            print(f"Health updated successfully")
            return jsonify({'success': True, 'message': f'Health set to {health}/{MAX_PLAYER_HEALTH}'})

        return jsonify({'error': 'Failed to update health', 'code': 'UPDATE_FAILED'}), 500
    except Exception as e:
        print(f"Error in update_health: {e}")
        return jsonify({'error': 'Server error', 'code': 'SERVER_ERROR'}), 500


@api_bp.route('/server/<server_id>/settings', methods=['GET'])
@auth_required
def get_server_settings(server_id):
    session_server_id = session.get('server_id')

    if session_server_id is None or str(session_server_id) != str(server_id):
        return jsonify({'error': 'Access Denied', 'code': 'PERMISSION_DENIED'}), 403

    try:
        settings = {
            'max_health': MAX_PLAYER_HEALTH,
            'server_id': server_id
        }
        return jsonify(settings)
    except Exception as e:
        print(f"Error fetching settings: {e}")
        return jsonify({'error': 'Failed to fetch settings', 'code': 'FETCH_ERROR'}), 500


@api_bp.route('/server/<server_id>/ore-probability', methods=['POST'])
@auth_required
def update_ore_probability(server_id):
    session_server_id = session.get('server_id')
    print(f"Ore Probability - Comparing: URL server_id={server_id}, Session server_id={session_server_id}")

    if session_server_id is None or str(session_server_id) != str(server_id):
        print(f"Server ID mismatch")
        return jsonify({'error': 'Access Denied', 'code': 'PERMISSION_DENIED'}), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request body', 'code': 'INVALID_REQUEST'}), 400

        ore_type = data.get('ore_type')
        probability = data.get('probability')

        print(f"Update Ore: {ore_type}, Probability: {probability}")

        if not ore_type or not isinstance(probability, (int, float)):
            return jsonify({'error': 'Invalid ore type or probability', 'code': 'INVALID_INPUT'}), 400

        if 0 <= probability <= 100:
            if db.update_ore_probability(int(server_id), ore_type, probability):
                print(f"Updated Successfully: {ore_type} = {probability}%")
                return jsonify({'success': True, 'message': f'{ore_type} updated to {probability}%'})

        print(f"Probability out of range: {probability}")
        return jsonify({'error': 'Probability must be between 0-100', 'code': 'INVALID_RANGE'}), 400
    except Exception as e:
        print(f"Error in update_ore_probability: {e}")
        return jsonify({'error': 'Server error', 'code': 'SERVER_ERROR'}), 500


@api_bp.route('/server/<server_id>/probabilities', methods=['GET'])
@auth_required
def get_probabilities(server_id):
    session_server_id = session.get('server_id')
    print(f"Get Probabilities - Comparing: URL server_id={server_id}, Session server_id={session_server_id}")

    if session_server_id is None or str(session_server_id) != str(server_id):
        print(f"Server ID mismatch")
        return jsonify({'error': 'Access Denied', 'code': 'PERMISSION_DENIED'}), 403

    try:
        probs = db.get_ore_probabilities(int(server_id))
        if not probs:
            return jsonify({'error': 'Probabilities not found', 'code': 'NOT_FOUND'}), 404
        return jsonify(probs)
    except Exception as e:
        print(f"Error fetching probabilities: {e}")
        return jsonify({'error': 'Failed to fetch probabilities', 'code': 'FETCH_ERROR'}), 500