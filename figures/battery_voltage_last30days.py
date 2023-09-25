import plotly.graph_objects as go
import pandas as pd
from . import update_figs_layout
import streamlit as st



@st.cache_data
def battery_voltage(data: pd.DataFrame):
    fig = go.Figure()
    color_list = ['#C47EF2', '#4EF2F2', '#F28A4E', '#DDF25A']
    for idx, bu in enumerate(data['name'].unique()):
        filtered_bu = data[data['name']==bu]

        fig.add_trace(go.Scatter(x=filtered_bu['snapshot_date'], y=filtered_bu['battery_voltage_mean'], mode='lines+markers',
                                 line=dict(width=2, color=color_list[idx], shape='spline'),
                                 name=filtered_bu['name'].unique()[0]))
    
    fig.update_layout(title=dict(text='Battery voltage over the last 30 days', x=0.5, y=0.93, xanchor='center', yanchor='top',
                                 font=dict(family='roboto', size=26)), showlegend=False, height=500,
                                 margin=dict(pad=0.2))
    
    fig.update_xaxes(showgrid=True, griddash='solid', gridcolor='rgba(211, 211, 211, 0.2)', title=None, tickfont=dict(size=16, family='roboto'))
    fig.update_yaxes(title=None, tickfont=dict(family='roboto', size=14), ticksuffix='V')

    update_figs_layout.alter_hover(fig=fig, mode='x unified')
    update_figs_layout.alter_legend(fig=fig, title='Metrics')
        
    return fig
