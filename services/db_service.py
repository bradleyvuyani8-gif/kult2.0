import sqlite3
from flask import g

DATABASE = 'database/store.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db(app):
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        phone TEXT,
                        address TEXT)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS carts (
                        user_id INTEGER,
                        product_id TEXT,
                        variant_id TEXT,
                        quantity INTEGER)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS coupons (
                        code TEXT PRIMARY KEY,
                        discount REAL,
                        active INTEGER)''')
        db.commit()
