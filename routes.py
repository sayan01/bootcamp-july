from flask import render_template, request, redirect, url_for, session, flash
from models import User, Category, Product, Cart, Transaction, Order, db
from main import app
from functools import wraps

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id', None)
        if not user_id:
            flash("Please login to continue!")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
@login_required
def home():
    user_id = session.get('user_id', None)
    user = User.query.get(user_id)
    return render_template('home.html', user=user)

@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id', None)
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

@app.route('/update_username', methods=['POST'])
@login_required
def update_username():
    user_id = session.get('user_id', None)
    user = User.query.get(user_id)
    username = request.form.get('username')
    user_exists = User.query.filter_by(username=username).first()
    if user_exists:
        flash("Username already exists!")
        return redirect(url_for('profile'))
    user.username = username
    db.session.commit()
    flash("Username updated successfully!")
    return redirect(url_for('profile'))

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        flash("Invalid username or password!")
        return redirect(url_for('login'))
    
    session['user_id'] = user.id
    return redirect(url_for('home'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')

    if not name or not username or not password:
        flash("All fields are required!")
        return redirect(url_for('register'))
    
    user = User.query.filter_by(username=username).first()
    if user:
        flash("Username already exists!")
        return redirect(url_for('register'))

    user = User(name=name, username=username, password=password)
    db.session.add(user)
    db.session.commit()
    flash("User registered successfully!")
    return redirect(url_for('login'))

