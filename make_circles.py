from geopy.distance import geodesic

def make_circles(radius, point_numbers, lat, long):
    circle_points = []
    poligono_teste = []
    for bearing in range(0, 361, 10): # são formados 37 pares de coordenadas
        point = geodesic(meters=radius).destination((lat, long), bearing)
        circle_points.append((point.latitude, point.longitude))
        poligono_teste.append(tuple([point.latitude, point.longitude]))

    return circle_points