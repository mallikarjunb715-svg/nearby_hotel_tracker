import pymysql
import requests

# Connect to MySQL database
db = pymysql.connect(
    host='localhost',
    user='root',
    password='Virat',
    database='foodserve',
    cursorclass=pymysql.cursors.DictCursor
)

# Target Bangalore central coordinates (bounding box) to avoid API timeout
overpass_url = "https://overpass-api.de/api/interpreter"
overpass_query = """
[out:json][timeout:25];
(
  node["amenity"="restaurant"](12.91,77.56,12.99,77.65);
);
out body 20;
"""

headers = {
    'User-Agent': 'FoodNearMeApp/1.0 (Python requests)'
}

print("Fetching Bangalore restaurant data...")
try:
    response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    cuisines = ['South Indian', 'North Indian', 'Chinese', 'Biryani', 'Continental', 'Italian']
    sample_images = [
        'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500',
        'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=500',
        'https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=500'
    ]

    with db.cursor() as cursor:
        count = 0
        for item in data.get('elements', []):
            tags = item.get('tags', {})
            name = tags.get('name')
            if not name:
                continue
                
            cuisine = tags.get('cuisine', cuisines[count % len(cuisines)]).capitalize()
            street = tags.get('addr:street') or tags.get('addr:suburb') or 'Koramangala, Bangalore'
            rating = round(4.0 + (count % 10) * 0.1, 1)
            image_url = sample_images[count % len(sample_images)]

            cursor.execute(
                """INSERT INTO restaurants (name, cuisine, address, rating, image_url) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (name, cuisine, street, rating, image_url)
            )
            count += 1

        db.commit()
        print(f"Success! Inserted {count} real Bangalore restaurants into your database.")

except Exception as e:
    print(f"API Error: {e}")
finally:
    db.close()