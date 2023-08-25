import plotly.graph_objects as go
import streamlit as st
from . import update_figs_layout

@st.cache_data
def analise_descritiva(data):
    map_colors = ['#5FE867', '#69FFF1', '#6B90E8', '#B469FF', '#F564A2', '#E89482', '#E8C36B']
    fig = go.Figure()
    counter = 0
    for metric in data['metricas']:
        subset = data[data['metricas']==metric]
        fig.add_trace(go.Bar(x=subset['metricas'], y=subset['IEF'], name=metric, marker=dict(color=map_colors[counter])))
        counter += 1

    fig.update_layout(title=dict(text='SLA Descriptive analysis', xanchor='center', yanchor='top', x=0.5, y=0.98, font=dict(size=30, color='whitesmoke')),
                      font=dict(family='roboto'), uniformtext_minsize=26, height=580, template='plotly')
    fig.update_traces(textposition='outside', textfont_size=16)
    fig.update_xaxes(title=dict(text='Metrics', font=dict(size=18, family='roboto')), showticklabels=True, tickfont=dict(size=16, family='roboto'), showline=True, linewidth=1)
    fig.update_yaxes(title=dict(text='SLA', font=dict(size=18, family='roboto')), showticklabels=True, tickfont=dict(size=16, family='roboto'), showline=True, linewidth=1,
                     gridcolor='rgba(222, 223, 222, 0.1)')

    update_figs_layout.alter_hover(fig=fig)
    return fig
