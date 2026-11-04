from flask import Flask
from config import Config
from routes.main_routes import main_bp
from routes.admin_routes import admin_bp
from services.db_service import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize SQLite database for local persistence
    init_db(app)

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
