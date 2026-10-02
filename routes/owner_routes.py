import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from utils.db import get_db

owner_bp = Blueprint('owner', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@owner_bp.route('/add-restaurant', methods=['GET', 'POST'])
def add_restaurant():
    if request.method == 'POST':
        name = request.form.get('name')
        city = request.form.get('city')
        address = request.form.get('address')
        cuisine = request.form.get('cuisine', 'General')  # Added fallback default
        description = request.form.get('description')
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        
        file = request.files.get('image')
        filename = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        db = get_db()
        with db.cursor() as cursor:
            query = """
                INSERT INTO restaurants (name, city, address, cuisine, description, latitude, longitude, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, city, address, cuisine, description, latitude, longitude, filename))
            db.commit()

        flash("Restaurant added successfully!", "success")
        return redirect(url_for('home'))

    return render_template('add_restaurant.html')