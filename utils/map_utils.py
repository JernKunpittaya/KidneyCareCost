import folium
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two geographic coordinates using the Haversine formula.

    Args:
        lat1, lon1: Latitude and longitude of the first point
        lat2, lon2: Latitude and longitude of the second point

    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences in coordinates
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

def create_map(center_lat=13.7563, center_lon=100.5018):
    """Create a Folium map centered on the specified coordinates."""
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles="OpenStreetMap"
    )
    return m