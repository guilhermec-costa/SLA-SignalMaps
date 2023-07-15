import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def get_mapbox_token() -> str:
    with open('mapbox_token.txt') as token:
        return token.read()

def check_bubble_size(type_of_group: str) -> dict.values:
    dinamic_sizes = {'Pontos instalados': 45, 'IEF': 20}
    return dinamic_sizes.get(type_of_group)

def add_traces_on_map(fig, another_data, name, fillcolor: str = 'rgba(255, 0, 0, 0.3)') -> None:
    fig.add_trace(go.Scattermapbox(lat=another_data['Latitude'], lon=another_data['Longitude'],
                                   mode='lines', line=dict(color=fillcolor), fill='toself', name=name))

def plot_sla_map(data_sla: pd.DataFrame, title: str, colmn_to_base_color = None, theme: str = 'carto-darkmatter', group_type: str = None):
    
    bubble_size = check_bubble_size(group_type)
    fig = px.scatter_mapbox(data_sla, lat='Latitude', lon='Longitude', color=colmn_to_base_color, color_continuous_scale=px.colors.sequential.Viridis, height=750,
                            size=group_type, size_max=bubble_size, center=dict(lat=-23.5607, lon=-46.8171), zoom=8, opacity=0.95, hover_name='Grupo - Nome')
    fig.update_layout(title=dict(text=title, xanchor='center', yanchor='top', x=0.5, y=0.98, font=dict(size=25, color='whitesmoke')),
                    font=dict(family='roboto'), mapbox=dict(accesstoken=get_mapbox_token(),
                                                            style=theme), legend=dict(orientation='h', yanchor='bottom', y=-0.2))
    
    return fig