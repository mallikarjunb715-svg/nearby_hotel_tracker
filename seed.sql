USE foodnearme_db;

-- Admin Passwords are 'admin123' (bcrypt hashed)
-- Owner Passwords are 'owner123'
-- Customer Passwords are 'cust123'
INSERT INTO users (id, name, email, phone, password_hash, role) VALUES
(1, 'System Admin', 'admin@foodnearme.com', '9999999999', '$2b$12$e7.fQ0gL8V1yN6gK1u9.3u2Kz2W7U0sS9oK1u9.3u2Kz2W7U0sS9o', 'admin'),
(2, 'Rahul Owner', 'rahul@grandpalace.com', '9876543210', '$2b$12$e7.fQ0gL8V1yN6gK1u9.3u2Kz2W7U0sS9oK1u9.3u2Kz2W7U0sS9o', 'owner'),
(3, 'Priya Owner', 'priya@spicegarden.com', '9876543211', '$2b$12$e7.fQ0gL8V1yN6gK1u9.3u2Kz2W7U0sS9oK1u9.3u2Kz2W7U0sS9o', 'owner'),
(4, 'John Customer', 'john@gmail.com', '9876543212', '$2b$12$e7.fQ0gL8V1yN6gK1u9.3u2Kz2W7U0sS9oK1u9.3u2Kz2W7U0sS9o', 'customer');

INSERT INTO food_categories (id, name, icon_class) VALUES
(1, 'Biryani', 'bi-fire'),
(2, 'South Indian', 'bi-disc'),
(3, 'North Indian', 'bi-square-fill'),
(4, 'Chinese', 'bi-box-seam'),
(5, 'Desserts', 'bi-cup-straw'),
(6, 'Beverages', 'bi-cup-hot');

INSERT INTO hotels (id, owner_id, name, description, address, phone, latitude, longitude, opening_time, closing_time, is_verified, is_approved) VALUES
(1, 2, 'Grand Palace Restaurant', 'Best Biryani & Mughlai Dishes in town.', '123 MG Road, Bengaluru', '080-12345678', 12.97159870, 77.59456270, '10:00:00', '23:00:00', 1, 1),
(2, 3, 'Spice Garden', 'Authentic South & North Indian Delicacies.', '45 Indiranagar, Bengaluru', '080-87654321', 12.97836920, 77.64083560, '08:00:00', '22:30:00', 1, 1);

INSERT INTO foods (id, hotel_id, category_id, name, description, price, is_veg, is_available, views_count) VALUES
(1, 1, 1, 'Chicken Dum Biryani', 'Aromatic Basmati Rice cooked with tender chicken pieces and spices.', 240.00, 0, 1, 120),
(2, 1, 3, 'Paneer Butter Masala', 'Rich and creamy curry with soft paneer cubes.', 180.00, 1, 1, 85),
(3, 2, 1, 'Special Chicken Biryani', 'Hyderabadi style spicy dum biryani served with raita.', 210.00, 0, 1, 95),
(4, 2, 2, 'Masala Dosa', 'Crispy dosa with delicious potato masala inside.', 80.00, 1, 1, 150);

INSERT INTO reviews (user_id, hotel_id, food_id, rating, review_text) VALUES
(4, 1, 1, 9.2, 'Absolutely flavorful biryani! Generous portion size.'),
(4, 2, 4, 8.5, 'Crispy and hot dosa. Sambhar was very tasty!');

INSERT INTO offers (hotel_id, title, description, discount_percentage, valid_till) VALUES
(1, 'Flat 15% OFF', 'Get 15% off on orders above Rs. 500', 15.00, '2026-12-31'),
(2, 'Morning Breakfast Combo', 'Buy 2 Dosas & get free filter coffee', 10.00, '2026-12-31');