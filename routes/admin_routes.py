from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.db import get_db

# Make sure this variable name is EXACTLY admin_bp
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def admin_dashboard():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM restaurants")
        restaurants = cursor.fetchall()
    return render_template('admin/dashboard.html', restaurants=restaurants)