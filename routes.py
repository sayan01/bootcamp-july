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

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id', None)
        if not user_id:
            flash("Please login to continue!")
            return redirect(url_for('login'))
        user = User.query.get(user_id)
        if not user:
            flash("User not found!")
            return redirect(url_for('login'))
        if not user.is_admin:
            flash("You are not authorized to view this page!")
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
@login_required
def home():
    user_id = session.get('user_id', None)
    user = User.query.get(user_id)
    if user.is_admin:
        return redirect(url_for('admin'))
    categories = Category.query.all()
    return render_template('home.html', user=user, categories=categories)

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


@app.route('/admin')
@admin_required
def admin():
    user_id = session.get('user_id', None)
    user = User.query.get(user_id)
    if not user.is_admin:
        flash("You are not authorized to view this page!")
        return redirect(url_for('home'))
    categories = Category.query.all()
    users = User.query.all()
    return render_template('admin.html', current_user=user, categories=categories, users=users)

@app.route('/user/<int:user_id>/delete')
@admin_required
def user_delete(user_id):
    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        flash("User not found!")
        return redirect(url_for('admin'))
    if user_to_delete.is_admin:
        flash("Cannot delete admin!")
        return redirect(url_for('admin'))
    return render_template('admin/user_delete.html', user=user_to_delete)

@app.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def user_delete_post(user_id):
    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        flash("User not found!")
        return redirect(url_for('admin'))
    if user_to_delete.is_admin:
        flash("Cannot delete admin!")
        return redirect(url_for('admin'))
    db.session.delete(user_to_delete)
    db.session.commit()
    flash("User deleted successfully!")
    return redirect(url_for('admin'))

@app.route('/category/add')
@admin_required
def category_add():
    return render_template('admin/category_add.html')

@app.route('/category/add', methods=['POST'])
@admin_required
def category_add_post():
    name = request.form.get('name')
    description = request.form.get('description')
    if not name:
        flash("Name is required!")
        return redirect(url_for('category_add'))
    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()
    flash("Category added successfully!")
    return redirect(url_for('admin'))

@app.route('/category/<int:category_id>/delete')
@admin_required
def category_delete(category_id):
    category = Category.query.get(category_id)
    if not category:
        flash("Category not found!")
        return redirect(url_for('admin'))
    return render_template('admin/category_delete.html', category=category)

@app.route('/category/<int:category_id>/delete', methods=['POST'])
@admin_required
def category_delete_post(category_id):
    category = Category.query.get(category_id)
    if not category:
        flash("Category not found!")
        return redirect(url_for('admin'))
    db.session.delete(category)
    db.session.commit()
    flash("Category deleted successfully!")
    return redirect(url_for('admin'))

@app.route('/category/<int:category_id>/edit')
@admin_required
def category_edit(category_id):
    category = Category.query.get(category_id)
    if not category:
        flash("Category not found!")
        return redirect(url_for('admin'))
    return render_template('admin/category_edit.html', category=category)

@app.route('/category/<int:category_id>/edit', methods=['POST'])
@admin_required
def category_edit_post(category_id):
    category = Category.query.get(category_id)
    if not category:
        flash("Category not found!")
        return redirect(url_for('admin'))
    name = request.form.get('name')
    description = request.form.get('description')
    if not name:
        flash("Name is required!")
        return redirect(url_for('category_edit', category_id=category_id))
    category.name = name
    category.description = description
    db.session.commit()
    flash("Category updated successfully!")
    return redirect(url_for('admin'))

@app.route('/category/<int:category_id>')
@admin_required
def product_list(category_id):
    category = Category.query.get(category_id)
    if not category:
        flash("Category not found!")
        return redirect(url_for('admin'))
    return render_template('admin/product_list.html', category=category)

@app.route('/product/add')
@admin_required
def product_add():
    categories = Category.query.all()
    category_id = request.args.get('category_id', None)
    if category_id:
        category_id = int(category_id)
        return render_template('admin/product_add.html', categories=categories, category_id=category_id)
    return render_template('admin/product_add.html', categories=categories)

@app.route('/product/add', methods=['POST'])
@admin_required
def product_add_post():
    name = request.form.get('name')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    category_id = request.form.get('category')
    if not name or not price or not quantity or not category_id:
        flash("All fields are required!")
        return redirect(url_for('product_add'))

    try:
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        flash("Price and Quantity must be numbers!")
        return redirect(url_for('product_add'))

    category = Category.query.get(category_id)
    if not category:
        flash("Category not found!")
        return redirect(url_for('product_add'))

    product = Product(name=name, price=price, quantity=quantity, category=category)
    db.session.add(product)
    db.session.commit()
    flash("Product added successfully!")
    return redirect(url_for('admin'))

@app.route('/product/<int:product_id>/edit')
@admin_required
def product_edit(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found!")
        return redirect(url_for('admin'))
    categories = Category.query.all()
    return render_template('admin/product_edit.html', product=product, categories=categories)

@app.route('/product/<int:product_id>/edit', methods=['POST'])
@admin_required
def product_edit_post(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found!")
        return redirect(url_for('admin'))
    name = request.form.get('name')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    category_id = request.form.get('category')
    if not name or not price or not quantity or not category_id:
        flash("All fields are required!")
        return redirect(url_for('product_edit', product_id=product_id))

    try:
        price = float(price)
        quantity = int(quantity)
    except ValueError:
        flash("Price and Quantity must be numbers!")
        return redirect(url_for('product_edit', product_id=product_id))

    category = Category.query.get(category_id)
    if not category:
        flash("Category not found!")
        return redirect(url_for('product_edit', product_id=product_id))

    product.name = name
    product.price = price
    product.quantity = quantity
    product.category = category
    db.session.commit()
    flash("Product updated successfully!")
    return redirect(url_for('admin'))

@app.route('/product/<int:product_id>/delete')
@admin_required
def product_delete(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found!")
        return redirect(url_for('admin'))
    return render_template('admin/product_delete.html', product=product)

@app.route('/product/<int:product_id>/delete', methods=['POST'])
@admin_required
def product_delete_post(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found!")
        return redirect(url_for('admin'))
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully!")
    return redirect(url_for('admin'))

# user routes

@app.route('/product/<int:product_id>/add_to_cart', methods=['POST'])
@login_required
def add_to_cart(product_id):
    user_id = session.get('user_id', None)
    user = User.query.get(user_id)
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found!")
        return redirect(url_for('home'))
    quantity = request.form.get('quantity')
    if not quantity:
        flash("Quantity is required!")
        return redirect(url_for('home'))
    try:
        quantity = int(quantity)
    except ValueError:
        flash("Quantity must be a number!")
        return redirect(url_for('home'))
    cart = Cart.query.filter_by(user=user, product=product).first()
    if cart:
        cart.quantity += quantity
    else:
        cart = Cart(user=user, product=product, quantity=quantity)
        db.session.add(cart)
    db.session.commit()
    flash("Product added to cart!")
    return redirect(url_for('home'))

@app.route('/cart')
@login_required
def cart():
    user_id = session.get('user_id', None)
    user = User.query.get(user_id)
    total = sum([cart.product.price * cart.quantity for cart in user.carts])
    return render_template('cart.html', user=user, total=total)

@app.route('/cart/<int:cart_id>/delete')
@login_required
def cart_delete(cart_id):
    user = User.query.get(session.get('user_id', None))
    cart = Cart.query.get(cart_id)
    if not cart:
        flash("Cart not found!")
        return redirect(url_for('cart'))
    if cart.user != user:
        flash("You are not authorized to delete this cart!")
        return redirect(url_for('cart'))
    db.session.delete(cart)
    db.session.commit()
    flash("Product deleted from cart successfully!")
    return redirect(url_for('cart'))
