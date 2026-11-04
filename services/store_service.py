import sqlite3
import os
from flask import current_app

class StoreService:
    @staticmethod
    def get_db():
        db_path = os.path.join(current_app.config['BASE_DIR'], 'database.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def init_db():
        conn = StoreService.get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                subscribed INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carts (
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coupons (
                code TEXT PRIMARY KEY,
                discount_pct INTEGER NOT NULL,
                status TEXT DEFAULT 'active'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                email TEXT PRIMARY KEY,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    @staticmethod
    def register_user(name, email, password):
        try:
            conn = StoreService.get_db()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (name, email, password, subscribed) VALUES (?, ?, ?, 1)', (name, email, password))
            cursor.execute('INSERT OR IGNORE INTO subscribers (email) VALUES (?)', (email,))
            conn.commit()
            conn.close()
            return True, "Account registered successfully."
        except sqlite3.IntegrityError:
            return False, "Email already exists in database."

    @staticmethod
    def authenticate_user(email, password):
        conn = StoreService.get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def save_user_cart(user_id, cart_items):
        conn = StoreService.get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM carts WHERE user_id = ?', (user_id,))
        for item in cart_items:
            cursor.execute('INSERT INTO carts (user_id, product_id, quantity) VALUES (?, ?, ?)',
                           (user_id, item['id'], item['quantity']))
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_cart(user_id):
        conn = StoreService.get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT product_id as id, quantity FROM carts WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
