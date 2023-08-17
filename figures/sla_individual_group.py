import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from . import update_figs_layout
import streamlit as st

@st.cache_data
def sla_last_30days_individual(data: pd.DataFrame):
    fig = go.Figure()
    color_list = ['#C47EF2', '#4EF2F2', '#F28A4E', '#DDF25A']
    fig.add_trace(go.Scatter(x=data['data snapshot'], y=data['IEF']))

    fig.update_layout(title=dict(text='Average SLA over the last 30 days', font=dict(size=26, family='roboto'), x=0.5, y=0.93, xanchor='center', yanchor='top'),
                                            font=dict(family='roboto'), colorscale_sequential=px.colors.qualitative.G10,
                      legend=dict(y=-0.2, orientation='h', font=dict(family='roboto', size=14)), height=500)
    
    fig.update_xaxes(showgrid=True, griddash='solid', gridcolor='rgba(211, 211, 211, 0.2)', title=None, tickfont=dict(size=16, family='roboto'))
    fig.update_yaxes(title=dict(text=None, font=dict(family='roboto', size=18)), tickfont=dict(family='roboto', size=14), ticksuffix='%')

    update_figs_layout.alter_hover(fig=fig, mode='x unified')

    return fig

