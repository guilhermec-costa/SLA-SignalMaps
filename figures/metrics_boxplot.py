import plotly.graph_objects as go
import numpy as np
import datetime
import streamlit as st
from . import update_figs_layout

@st.cache_data
def metrics_boxplot(data):
    fig = go.Figure()
    fig.add_trace(go.Box(x=data['snapshot_date'], y=data['sla_mean'], boxmean='sd', marker=dict(color='#51DB91')))
    fig.update_yaxes(title=dict(text='Average SLA %', font=dict(size=16, family='roboto')))
    fig.update_layout(font=dict(family='roboto'), title=dict(text='SLA metrics over the last 30 days', x=0.5, y=0.93, xanchor='center', yanchor='top',
                                                             font=dict(family='roboto', size=26)), height=500,
                    )
    
    fig.update_xaxes(tickfont=dict(size=16, family='roboto'), rangeslider_visible=True, range=[np.min(data['snapshot_date'] - datetime.timedelta(days=1)),
                                                                                               np.max(data['snapshot_date']) + datetime.timedelta(days=1)])
    fig.update_yaxes(title=None, tickfont=dict(family='roboto', size=14), ticksuffix='%')
    # go.layout.XAxis.autorange()
    update_figs_layout.alter_hover(fig=fig, mode='x unified')
    update_figs_layout.alter_legend(fig=fig, title='Metrics')

    return fig