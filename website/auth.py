from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Users, session
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, cursor
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

ADMIN_PASSWORD = '123456789admin'

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        fetch_user = session.query(Users).filter_by(email = email).first()

        if fetch_user:
            if check_password_hash(fetch_user.password, password):
                login_user(fetch_user, remember = True)
                flash('Logged in successfully', category = 'success')
                return redirect(url_for('views.home')) 
            else:
                flash('Incorrect password, try again.', category = 'error')
                return redirect(url_for('auth.login')) 
        else:
            flash('User does not exist.', category = 'error')
            return redirect(url_for('auth.login')) 

    return render_template("login.html", user = current_user)

@auth.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods = ['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        cursor.execute('SELECT * FROM users WHERE email = ? OR username = ?', (email, username))
        user = cursor.fetchone()
        if password1 == ADMIN_PASSWORD:
            admin = 1
        else:
            admin = 0 
        if user: 
            if user[1] == email:
                flash('An account with the same email already exists.', category = 'error')
            elif user[2]:
                flash('An account with the same username already exists.', category = 'error')
        elif len(email) < 4:
            flash('Email must be longer than 3 characters.', category = 'error')
        elif len(username) < 4:
            flash('Username must be longer than 3 characters.', category = 'er  ror')
        elif password1 != password2:
            flash('Passwords don\'t match.', category = 'error')
        elif len(password1) < 4:
            flash('Password must be longer than 3 characters.', category = 'error')
        else:
            cursor.execute('INSERT INTO users (email, username, password, admin) VALUES (?, ?, ?, ?)', 
                            (email, username, generate_password_hash(password1, method = 'pbkdf2:sha256'), admin))
            db.commit()
            
            cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
            user_id = cursor.fetchone()
            user_auth = session.query(Users).filter_by(email = email).first()

            login_user(user_auth, remember = True)
            flash('Account created!', category = 'success')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user = current_user)