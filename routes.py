from flask import render_template, request, redirect, url_for, session, flash
from models import User, Category, Product, Cart, Transaction, Order, db
from main import app

@app.route('/')
def home():
    user_id = session.get('user_id', None)
    user = None
    if user_id:
        user = User.query.get(user_id)
    return render_template('home.html', user=user)

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

