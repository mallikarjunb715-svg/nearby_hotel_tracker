from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash
from app import get_db
from utils.geo import haversine_distance
from utils.recommendation import calculate_recommendation_score
from utils.auth import login_required
import os
from werkzeug.utils import secure_filename

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/')
def index():
    user_lat = request.args.get('lat', type=float, default=12.97159870)
    user_lng = request.args.get('lng', type=float, default=77.59456270)
    
    db = get_db()
    cursor = db.cursor()

    # Get Categories
    cursor.execute("SELECT * FROM food_categories")
    categories = cursor.fetchall()

    # Get Top Rated & Popular Foods with Distances
    cursor.execute("""
        SELECT f.*, h.name as hotel_name, h.latitude, h.longitude,
               COALESCE(AVG(r.rating), 0) as avg_rating,
               COUNT(r.id) as review_count
        FROM foods f
        JOIN hotels h ON f.hotel_id = h.id
        LEFT JOIN reviews r ON f.id = r.food_id
        WHERE h.is_approved = 1 AND f.is_available = 1
        GROUP BY f.id
        LIMIT 12
    """)
    foods = cursor.fetchall()

    for item in foods:
        item['distance'] = haversine_distance(user_lat, user_lng, item['latitude'], item['longitude'])
        item['score'] = calculate_recommendation_score(item['avg_rating'], item['distance'], item['price'], item['views_count'])

    # Sort by Recommendation Score
    foods = sorted(foods, key=lambda x: x['score'], reverse=True)

    return render_template('index.html', categories=categories, foods=foods, user_lat=user_lat, user_lng=user_lng)

@customer_bp.route('/compare')
def compare():
    query = request.args.get('q', '').strip()
    user_lat = request.args.get('lat', type=float, default=12.97159870)
    user_lng = request.args.get('lng', type=float, default=77.59456270)
    max_radius = request.args.get('radius', type=float, default=10.0)

    db = get_db()
    cursor = db.cursor()

    results = []
    if query:
        cursor.execute("""
            SELECT f.*, h.id as hotel_id, h.name as hotel_name, h.latitude, h.longitude, h.address,
                   COALESCE(AVG(r.rating), 0) as avg_rating, COUNT(r.id) as review_count
            FROM foods f
            JOIN hotels h ON f.hotel_id = h.id
            LEFT JOIN reviews r ON f.id = r.food_id
            WHERE (f.name LIKE %s OR f.description LIKE %s) AND h.is_approved = 1
            GROUP BY f.id
        """, (f"%{query}%", f"%{query}%"))
        raw_items = cursor.fetchall()

        for item in raw_items:
            dist = haversine_distance(user_lat, user_lng, item['latitude'], item['longitude'])
            if dist <= max_radius:
                item['distance'] = dist
                item['rec_score'] = calculate_recommendation_score(item['avg_rating'], dist, item['price'], item['views_count'])
                results.append(item)

    return render_template('compare.html', results=results, query=query, user_lat=user_lat, user_lng=user_lng)

@customer_bp.route('/food/<int:food_id>', methods=['GET', 'POST'])
def food_detail(food_id):
    db = get_db()
    cursor = db.cursor()

    # Increment View Count
    cursor.execute("UPDATE foods SET views_count = views_count + 1 WHERE id = %s", (food_id,))
    db.commit()

    cursor.execute("""
        SELECT f.*, h.name as hotel_name, h.address, h.phone, h.latitude, h.longitude,
               COALESCE(AVG(r.rating), 0) as avg_rating, COUNT(r.id) as review_count
        FROM foods f
        JOIN hotels h ON f.hotel_id = h.id
        LEFT JOIN reviews r ON f.id = r.food_id
        WHERE f.id = %s
        GROUP BY f.id
    """, (food_id,))
    food = cursor.fetchone()

    cursor.execute("""
        SELECT r.*, u.name as user_name
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.food_id = %s
        ORDER BY r.created_at DESC
    """, (food_id,))
    reviews = cursor.fetchall()

    return render_template('food_detail.html', food=food, reviews=reviews)

@customer_bp.route('/review/submit', methods=['POST'])
@login_required
def submit_review():
    food_id = request.form['food_id']
    hotel_id = request.form['hotel_id']
    rating = float(request.form['rating'])
    review_text = request.form.get('review_text', '')
    user_id = session['user_id']

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO reviews (user_id, hotel_id, food_id, rating, review_text)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE rating = VALUES(rating), review_text = VALUES(review_text)
    """, (user_id, hotel_id, food_id, rating, review_text))
    
    db.commit()
    flash('Your review & rating have been saved!', 'success')
    return redirect(url_for('customer.food_detail', food_id=food_id))