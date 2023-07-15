import numpy as np
from geopy.distance import geodesic

constant = 6371000
def make_circles(radius, point_numbers, lat, long):
    circle_points = []
    for bearing in range(0, 361, 10):
        point = geodesic(meters=radius).destination((lat, long), bearing)
        circle_points.append((point.latitude, point.longitude))
    # angulos = np.linspace(0, 2 * np.pi, num=point_numbers)
    # lat_circle = lat + (radius/6371000) * np.sin(angulos)
    # lon_circle = long + (radius/6371000) * np.cos(angulos)

    return circle_points