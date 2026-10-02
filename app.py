from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY',
    'development-secret-key'
)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///foodnearme.db'
)

db = SQLAlchemy(app)
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            flash('Please login first.', 'warning')
            return redirect(url_for('login'))

        return f(*args, **kwargs)

    return decorated_function

# ==================== DATABASE MODELS ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cuisine = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(300), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    menus = db.relationship('MenuItem', backref='restaurant', lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='restaurant', lazy=True, cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='restaurant', lazy=True, cascade="all, delete-orphan")

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    delivery_address = db.Column(db.String(300), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Order Placed', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

# ==================== DATABASE SEEDING ====================

def seed_database():
    if not Restaurant.query.first():
        r1 = Restaurant(
            name="Spice Villa",
            cuisine="North Indian",
            address="123 MG Road",
            city="Bangalore",
            description="Authentic royal spices and rich traditional curries prepared fresh daily.",
            image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500&auto=format&fit=crop&q=60",
            latitude=13.0649,
            longitude=77.5002
        )
        r2 = Restaurant(
            name="Pizza Paradise",
            cuisine="Italian",
            address="456 Brigade Road",
            city="Bangalore",
            description="Wood-fired authentic Italian pizzas, hand-tossed crusts, and creamy pastas.",
            image_url="https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=500&auto=format&fit=crop&q=60",
            latitude=13.0750,
            longitude=77.5100
        )
        db.session.add_all([r1, r2])
        db.session.commit()
        
        m1 = MenuItem(name="Butter Chicken", price=14.99, restaurant_id=r1.id)
        m2 = MenuItem(name="Garlic Naan", price=3.49, restaurant_id=r1.id)
        m3 = MenuItem(name="Margherita Pizza", price=12.50, restaurant_id=r2.id)
        m4 = MenuItem(name="Pasta Alfredo", price=11.00, restaurant_id=r2.id)
        db.session.add_all([m1, m2, m3, m4])
        db.session.commit()

        # Seed sample demo order for admin panel testing
        sample_order = Order(
            restaurant_id=r1.id,
            delivery_address="789 Residency Road, Bangalore",
            total_amount=18.48,
            status="Preparing"
        )
        db.session.add(sample_order)
        db.session.commit()

        oi1 = OrderItem(order_id=sample_order.id, name="Butter Chicken", price=14.99, quantity=1)
        oi2 = OrderItem(order_id=sample_order.id, name="Garlic Naan", price=3.49, quantity=1)
        db.session.add_all([oi1, oi2])
        db.session.commit()

# ==================== APP ROUTES ====================

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    if search_query:
        restaurants = Restaurant.query.filter(
            (Restaurant.name.ilike(f'%{search_query}%')) |
            (Restaurant.city.ilike(f'%{search_query}%')) |
            (Restaurant.cuisine.ilike(f'%{search_query}%'))
        ).all()
    else:
        restaurants = Restaurant.query.all()
    return render_template('index.html', restaurants=restaurants)

@app.route('/admin')
@admin_required
def admin():
    restaurants = Restaurant.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).all()
    users_count = User.query.count()
    return render_template('admin.html', restaurants=restaurants, orders=orders, users_count=users_count)

@app.route('/restaurant/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    return render_template('restaurant.html', restaurant=restaurant)

@app.route('/add_restaurant', methods=['GET', 'POST'])
@admin_required
def add_restaurant():
    if request.method == 'POST':
        name = request.form.get('name')
        cuisine = request.form.get('cuisine')
        address = request.form.get('address')
        city = request.form.get('city')
        description = request.form.get('description')
        image_url = request.form.get('image_url', 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4')
        
        try:
            latitude = float(request.form.get('latitude')) if request.form.get('latitude') else None
            longitude = float(request.form.get('longitude')) if request.form.get('longitude') else None
        except ValueError:
            latitude, longitude = None, None

        new_restaurant = Restaurant(
            name=name, cuisine=cuisine, address=address, city=city,
            description=description, image_url=image_url,
            latitude=latitude, longitude=longitude
        )
        db.session.add(new_restaurant)
        db.session.commit()
        flash('Restaurant added successfully!', 'success')
        return redirect(url_for('admin'))
    
    return render_template('add_restaurant.html')

@app.route('/restaurant/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    if request.method == 'POST':
        restaurant.name = request.form.get('name')
        restaurant.cuisine = request.form.get('cuisine')
        restaurant.address = request.form.get('address')
        restaurant.city = request.form.get('city')
        restaurant.description = request.form.get('description')
        restaurant.image_url = request.form.get('image_url')
        db.session.commit()
        flash('Restaurant updated successfully!', 'success')
        return redirect(url_for('admin'))
    return render_template('edit_restaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:id>/delete', methods=['POST'])
@admin_required
def delete_restaurant(id):
    restaurant = Restaurant.query.get_or_404(id)
    db.session.delete(restaurant)
    db.session.commit()
    flash('Restaurant deleted successfully.', 'info')
    return redirect(url_for('admin'))

@app.route('/restaurant/<int:restaurant_id>/add_review', methods=['POST'])
def add_review(restaurant_id):
    rating = float(request.form.get('rating', 5.0))
    comment = request.form.get('comment', '')
    review = Review(rating=rating, comment=comment, restaurant_id=restaurant_id)
    db.session.add(review)
    db.session.commit()
    flash('Review added successfully!', 'success')
    return redirect(url_for('restaurant_detail', restaurant_id=restaurant_id))

@app.route('/restaurant/<int:restaurant_id>/place_order', methods=['POST'])
def place_order(restaurant_id):
    address = request.form.get('delivery_address', '123 Main Street')
    total = float(request.form.get('total_amount', 25.00))
    
    new_order = Order(
        restaurant_id=restaurant_id,
        user_id=session.get('user_id'),
        delivery_address=address,
        total_amount=total,
        status='Order Placed'
    )
    db.session.add(new_order)
    db.session.commit()
    
    flash('Order placed successfully! Live delivery tracking initialized.', 'success')
    return redirect(url_for('restaurant_detail', restaurant_id=restaurant_id))

@app.route('/order/<int:order_id>/update_status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.id} status updated to {new_status}.', 'success')
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already registered.', 'warning')
            return redirect(url_for('login'))
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

with app.app_context():
    db.create_all()
    seed_database()


if __name__ == '__main__':
    app.run(debug=True, port=5000)