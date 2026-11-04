from flask import Blueprint, render_template, request, redirect, url_for, session, g
import json
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Load 3D products configuration
    data_path = os.path.join(os.path.dirname(__file__), '../data/products.json')
    products = []
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            products = json.load(f)
    return render_template('index.html', products=products)

@main_bp.route('/cart', methods=['GET', 'POST'])
def cart():
    # Handle shopping cart updates, quantities, and coupon applications
    if 'cart' not in session:
        session['cart'] = []
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            product_id = request.form.get('product_id')
            variant_id = request.form.get('variant_id')
            session['cart'].append({'product_id': product_id, 'variant_id': variant_id, 'quantity': 1})
            session.modified = True
        elif action == 'apply_coupon':
            coupon_code = request.form.get('coupon_code')
            # Coupon validation logic hooks here
            session['coupon'] = coupon_code
            session.modified = True
            
    return render_template('cart.html', cart=session.get('cart', []))

@main_bp.route('/checkout', methods=['POST'])
def checkout():
    # Handle order finalization and routing to fulfillment services
    shipping_address = {
        "first_name": request.form.get('first_name'),
        "last_name": request.form.get('last_name'),
        "email": request.form.get('email'),
        "phone": request.form.get('phone'),
        "address1": request.form.get('address1'),
        "city": request.form.get('city'),
        "country": "ZA",
        "zip": request.form.get('zip')
    }
    # Clear cart upon successful checkout submission trigger
    session.pop('cart', None)
    return redirect(url_for('main.index'))
