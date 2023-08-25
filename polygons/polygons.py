from geopy.distance import geodesic
from shapely.geometry import Polygon
from typing import Union
import streamlit as st 
import pandas as pd


@st.cache_data
def calculate_polygons(lat:float, long:float, radius:int) -> Polygon:
    circle_points = []
    for bearing in range(0, 361, 10): # são formados 37 pares de coordenadas
        point = geodesic(meters=radius).destination((lat, long), bearing)
        circle_points.append((point.latitude, point.longitude))
    
    return Polygon(circle_points), circle_points

def check_if_pol_contains(args) -> Union[int, None]:
    idx, ponto, polygon = args
    return idx if polygon.contains(ponto) else None


@st.cache_data()
def tmp_coordinates(tmp_lats, tmp_longs):
    return pd.DataFrame(data={'Latitude':tmp_lats, 'Longitude':tmp_longs})
