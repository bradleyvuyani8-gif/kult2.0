import sqlite3
import os
from flask import g, current_app

def get_db():
    """Establish and retrieve the SQLite database connection for the current request context."""
    if 'db' not in g:
        db_path = current_app.config['DATABASE_PATH']
        
        # Ensure the database directory exists before connecting
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    """Initialize the SQLite database schema and register teardown handlers."""
    app.teardown_appcontext(close_db)
    with app.app_context():
        db = get_db()
        
        # User accounts & profile data (matching Printify delivery requirements)
        db.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        phone TEXT,
                        address TEXT,
                        city TEXT,
                        zip TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Persistent shopping carts
        db.execute('''CREATE TABLE IF NOT EXISTS carts (
                        user_id INTEGER,
                        product_id TEXT,
                        variant_id TEXT,
                        quantity INTEGER,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')
        
        # Discount coupons and redemption states
        db.execute('''CREATE TABLE IF NOT EXISTS coupons (
                        code TEXT PRIMARY KEY,
                        discount REAL,
                        active INTEGER)''')
                        
        # Fulfillment logs for Printify API tracking
        db.execute('''CREATE TABLE IF NOT EXISTS fulfillment_logs (
                        order_id TEXT PRIMARY KEY,
                        external_id TEXT,
                        status TEXT,
                        response_payload TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                        
        db.commit()
