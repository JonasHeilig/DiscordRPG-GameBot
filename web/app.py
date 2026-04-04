from flask import Flask
from flask_cors import CORS
from config import FLASK_SECRET_KEY, DATABASE_PATH
from web.routes.auth import auth_bp
from web.routes.dashboard import dashboard_bp
from web.routes.api import api_bp
from bot.database.db_manager import DatabaseManager
import os
import sys


def create_app():
    web_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(web_dir, 'templates')
    static_dir = os.path.join(web_dir, 'static')

    print(f"Template Dir: {template_dir}")
    print(f"Static Dir: {static_dir}")

    if os.path.exists(template_dir):
        print(f"Templates found:")
        for f in os.listdir(template_dir):
            print(f"   - {f}")
    else:
        print(f"Templates Folder not found: {template_dir}")

    app = Flask(__name__,
                template_folder=template_dir,
                static_folder=static_dir)

    app.config['SECRET_KEY'] = FLASK_SECRET_KEY
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    CORS(app)

    try:
        db = DatabaseManager()
    except Exception as e:
        print(f"DB Error: {e}")

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def not_found(error):
        return "Site not found", 404

    @app.errorhandler(500)
    def server_error(error):
        return "Internal Serer Error", 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5505)
