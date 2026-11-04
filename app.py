from flask import Flask
from routes.main_routes import main_bp
from config import Config
from services.store_service import StoreService

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    with app.app_context():
        StoreService.init_db()

    app.register_blueprint(main_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=8000, debug=True)
