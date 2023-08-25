import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from typing import Union
from . import update_figs_layout

def get_mapbox_token() -> str:
    return st.secrets.mapbox.mapbox_token

def check_bubble_size(type_of_group: str) -> dict.values:
    dinamic_sizes = {'Pontos instalados': 50, 'IEF': 25}
    return dinamic_sizes.get(type_of_group)

@st.cache_data
def add_traces_on_map(fig, another_data, name=None, fillcolor: str = 'rgba(255, 205, 0, 0)') -> None:
    fig.add_trace(go.Scattermapbox(lat=another_data['Latitude'], lon=another_data['Longitude'],
                                   mode='lines', line=dict(color=fillcolor), fill='toself', name=name))

@st.cache_data
def plot_sla_map(data_sla: pd.DataFrame, title: str, colmn_to_base_color = None, theme: str = 'satellite-streets', group_type: Union[str, None] = None, include_bu_city_info: bool = True):
    if include_bu_city_info:
        hover_data = ['Unidade de Negócio - Nome', 'Endereço', 'IEF', 'Cidade - Nome']
    else:
        hover_data = ['Endereço', 'IEF']
    
    steps = [10,20,30,40,50,60,70,80,90,100]
    continuous_scale = [(0, 'red'),(0.5, 'yellow'),(1, 'green')]
    bubble_size = check_bubble_size(group_type)
    fig = px.scatter_mapbox(data_sla, lat='Latitude', lon='Longitude', color=colmn_to_base_color, color_continuous_scale=continuous_scale, height=750,
                            size=group_type, size_max=bubble_size, center=dict(lat=-23.5607, lon=-46.8171), zoom=8, opacity=0.95, hover_name='Grupo - Nome',
                                hover_data=hover_data)
    fig.update_layout(title=dict(text=title, xanchor='center', yanchor='top', x=0.5, y=0.98, font=dict(size=25, color='whitesmoke')),
                    font=dict(family='roboto'), mapbox=dict(accesstoken=get_mapbox_token(),
                                                            style=theme), legend=dict(orientation='h', yanchor='bottom', y=-0.15),
                                                            template='plotly')
    
    fig.update_coloraxes(colorbar=dict(thickness=30))
    update_figs_layout.alter_hover(fig=fig)
    return fig
