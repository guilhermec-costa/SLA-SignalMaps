from geopy.distance import geodesic
from shapely.geometry import Polygon

def calculate_polygons(lat, long, radius=1500):
    circle_points = []
    for bearing in range(0, 361, 10): # são formados 37 pares de coordenadas
        point = geodesic(meters=radius).destination((lat, long), bearing)
        circle_points.append((point.latitude, point.longitude))
    
    return Polygon(circle_points), circle_points

def check_if_pol_contains(args):
    idx, ponto, polygon = args
    if polygon.contains(ponto):
        return idx
    return None