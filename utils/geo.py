import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points
    on the Earth (specified in decimal degrees).
    """
    if None in (lat1, lon1, lat2, lon2):
        return 0.0

    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(float(lat2) - float(lat1))
    dlon = math.radians(float(lon2) - float(lon1))
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) *
         math.sin(dlon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)