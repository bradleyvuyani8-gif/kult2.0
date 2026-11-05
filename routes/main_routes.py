import os
import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, session

main_bp = Blueprint('main', __name__)

# Shared storage database path
DB_DIR = '/sdcard/KULTDATABASE'
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'store.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fullname TEXT, email TEXT UNIQUE, password TEXT)''')
    
    # Automatically fix existing tables missing the fullname column
    try:
        c.execute("SELECT fullname FROM users LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("DROP TABLE users")
        c.execute('''CREATE TABLE users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, fullname TEXT, email TEXT UNIQUE, password TEXT)''')
        
    conn.commit()
    conn.close()

init_db()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user'] = email
            return redirect(url_for('main.index'))
        return "Invalid credentials. <a href='/login'>Try again</a>"
        
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)", (fullname, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('main.login'))
        except sqlite3.IntegrityError:
            return "Email already registered. <a href='/login'>Login instead</a>"
            
    return render_template('login.html')
