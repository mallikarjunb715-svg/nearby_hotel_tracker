from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'customer')

        hashed_password = generate_password_hash(password)
        db = get_db()
        
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                    (username, email, hashed_password, role)
                )
                db.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Email already registered or error occurred.', 'danger')

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            if not user.get('is_approved', True):
                flash('Your owner account is currently pending admin approval.', 'warning')
                return redirect(url_for('auth.login'))

            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            # Role-based redirection
            if user['role'] == 'owner':
                return redirect(url_for('owner.dashboard'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))