import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kult-secure-termux-production-key-2026'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    PRODUCTS_FILE = os.path.join(BASE_DIR, 'data', 'products.json')
