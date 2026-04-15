from math import radians, cos, sin, asin, sqrt


def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return 6371000 * c


def is_within_radius(user_lat, user_lon, lab_lat, lab_lon, radius_meters):
    distance = haversine(user_lat, user_lon, lab_lat, lab_lon)
    return distance <= radius_meters, distance
