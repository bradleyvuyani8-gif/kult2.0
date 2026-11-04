import json
import os
from flask import Blueprint, render_template, request, jsonify, session, current_app
from services.geo_service import GeoService
from services.store_service import StoreService

main_bp = Blueprint('main', __name__)

def load_products():
    path = current_app.config['PRODUCTS_FILE']
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []

def save_products(products):
    path = current_app.config['PRODUCTS_FILE']
    with open(path, 'w') as f:
        json.dump(products, f, indent=4)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/legal')
def legal():
    return render_template('legal.html')

@main_bp.route('/admin')
def admin_panel():
    conn = StoreService.get_db()
    users = conn.execute('SELECT * FROM users').fetchall()
    coupons = conn.execute('SELECT * FROM coupons').fetchall()
    subscribers = conn.execute('SELECT * FROM subscribers').fetchall()
    conn.close()
    return render_template('admin.html', users=users, coupons=coupons, subscribers=subscribers, products=load_products())

@main_bp.route('/api/config', methods=['GET'])
def get_config():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if client_ip in ['127.0.0.1', '::1', 'localhost']:
        client_ip = '8.8.8.8'
    currency, rates = GeoService.get_currency_and_rates(client_ip)
    
    user_data = None
    user_cart = []
    if 'user_id' in session:
        user_data = {"id": session['user_id'], "name": session['user_name'], "email": session['user_email']}
        user_cart = StoreService.get_user_cart(session['user_id'])

    return jsonify({
        "currency": currency,
        "rates": rates,
        "products": load_products(),
        "logged_in_user": user_data,
        "saved_cart": user_cart
    })

@main_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    success, msg = StoreService.register_user(data.get('name'), data.get('email'), data.get('password'))
    return jsonify({"success": success, "message": msg})

@main_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = StoreService.authenticate_user(data.get('email'), data.get('password'))
    if user:
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        return jsonify({"success": True, "user": {"name": user['name'], "email": user['email']}})
    return jsonify({"success": False, "message": "Invalid credentials."})

@main_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

@main_bp.route('/api/cart/save', methods=['POST'])
def save_cart():
    if 'user_id' in session:
        data = request.json
        StoreService.save_user_cart(session['user_id'], data.get('cart', []))
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "User not authenticated"})

@main_bp.route('/api/apply-coupon', methods=['POST'])
def apply_coupon():
    code = request.json.get('code', '').strip()
    conn = StoreService.get_db()
    coupon = conn.execute('SELECT * FROM coupons WHERE code = ? AND status = "active"', (code,)).fetchone()
    if coupon:
        conn.execute('UPDATE coupons SET status = "redeemed" WHERE code = ?', (code,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "discount_pct": coupon['discount_pct']})
    conn.close()
    return jsonify({"success": False, "message": "Invalid or already redeemed coupon code."})

@main_bp.route('/api/admin/coupon', methods=['POST'])
def create_coupon():
    data = request.json
    conn = StoreService.get_db()
    conn.execute('INSERT OR REPLACE INTO coupons (code, discount_pct, status) VALUES (?, ?, "active")',
                 (data.get('code').upper(), int(data.get('discount'))))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@main_bp.route('/api/admin/product', methods=['POST'])
def save_product():
    prod = request.json
    products = load_products()
    existing = next((p for p in products if p['id'] == prod.get('id')), None)
    if existing:
        existing.update(prod)
    else:
        prod['id'] = len(products) + 1
        products.append(prod)
    save_products(products)
    return jsonify({"success": True, "products": products})
