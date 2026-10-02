def calculate_recommendation_score(rating, distance_km, price, popularity_views):
    """
    Recommendation Score Calculation Engine:
    --------------------------------------------------
    Score = (Rating Weight * 40) + 
            (Distance Weight * 30) + 
            (Price Weight * 20) + 
            (Popularity Weight * 10)

    - Rating Score (1-10 normalized to 0-1)
    - Distance Score (Closer is better, capped at 15km decay)
    - Price Score (Lower is better, normalized baseline 500)
    - Popularity Score (Based on food item views)
    """
    # 1. Rating Component (Max 10)
    norm_rating = float(rating) / 10.0 if rating else 0.5

    # 2. Distance Decay Component
    dist = float(distance_km)
    if dist <= 0:
        norm_distance = 1.0
    elif dist > 15:
        norm_distance = 0.05
    else:
        norm_distance = 1.0 - (dist / 15.0)

    # 3. Price Metric (Assuming average baseline of ₹500)
    p = float(price) if price else 200.0
    norm_price = max(0.0, 1.0 - (p / 800.0))

    # 4. Popularity
    views = float(popularity_views) if popularity_views else 0
    norm_pop = min(1.0, views / 500.0)

    # Weighted Sum
    score = (norm_rating * 0.40) + (norm_distance * 0.30) + (norm_price * 0.20) + (norm_pop * 0.10)
    return round(score * 100, 2)