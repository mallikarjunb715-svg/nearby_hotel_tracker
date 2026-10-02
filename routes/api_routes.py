from flask import Blueprint, request, jsonify
from app import get_db
from utils.geo import haversine_distance

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/nearby-hotels')
def get_nearby_hotels():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', type=float, default=5.0)

    if not lat or not lng:
        return jsonify({'error': 'Latitude and Longitude required'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, latitude, longitude, address, phone FROM hotels WHERE is_approved = 1")
    hotels = cursor.fetchall()

    nearby = []
    for h in hotels:
        dist = haversine_distance(lat, lng, h['latitude'], h['longitude'])
        if dist <= radius:
            h['distance'] = dist
            nearby.append(h)

    return jsonify(sorted(nearby, key=lambda x: x['distance']))