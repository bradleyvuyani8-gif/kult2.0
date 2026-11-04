from flask import Blueprint, render_template, request, redirect, url_for, current_app
import sqlite3
import os
import json

admin_bp = Blueprint('admin', __name__)

# Private secret route token accessible only by you
SECRET_ADMIN_ROUTE = "kult-secure-control-panel-9921"

def get_db_connection():
    db_path = current_app.config['DATABASE_PATH']
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@admin_bp.route(f'/{SECRET_ADMIN_ROUTE}')
def admin_dashboard():
    # Fetch core statistics and records for the admin panel
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    coupons = conn.execute('SELECT * FROM coupons').fetchall()
    conn.close()

    # Load local products catalog
    data_path = os.path.join(os.path.dirname(__file__), '../data/products.json')
    products = []
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            products = json.load(f)

    return render_template('admin.html', users=users, coupons=coupons, products=products)

@admin_bp.route(f'/{SECRET_ADMIN_ROUTE}/product/add', methods=['POST'])
def add_product():
    # Add a new product to the catalog
    data_path = os.path.join(os.path.dirname(__file__), '../data/products.json')
    products = []
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            products = json.load(f)

    new_product = {
        "id": request.form.get('product_id'),
        "name": request.form.get('name'),
        "price": float(request.form.get('price', 0)),
        "printify_product_id": request.form.get('printify_product_id'),
        "variant_id": request.form.get('variant_id'),
        "model_path": request.form.get('model_path', '/static/models/shirt.gltf')
    }
    products.append(new_product)

    with open(data_path, 'w') as f:
        json.dump(products, f, indent=4)

    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route(f'/{SECRET_ADMIN_ROUTE}/coupon/add', methods=['POST'])
def add_coupon():
    # Create or update a discount coupon
    code = request.form.get('code').upper()
    discount = float(request.form.get('discount', 0.0))
    active = 1 if request.form.get('active') == 'on' else 0

    conn = get_db_connection()
    conn.execute('INSERT OR REPLACE INTO coupons (code, discount, active) VALUES (?, ?, ?)',
                 (code, discount, active))
    conn.commit()
    conn.close()

    return redirect(url_for('admin.admin_dashboard'))
