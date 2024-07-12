from flask import render_template
from main import app

@app.route('/')
def hello_world():
    return 'Hello, World!' 

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

