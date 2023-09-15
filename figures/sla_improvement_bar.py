import plotly.graph_objects as go
from . import update_figs_layout
import streamlit as st

def sla_improvement(data, xaxes, yaxes):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data[xaxes], y=data[yaxes], text=data[yaxes], marker=dict(color=data[yaxes], colorscale='Viridis_r'),
                        textfont=dict(family='roboto', size=16)))
    
    fig.update_layout(title=dict(text='Possible points to improve per address',
                                    font=dict(family='roboto', size=26), x=0.5, y=0.93, yanchor='top', xanchor='center'))
    update_figs_layout.alter_hover(fig)
    update_figs_layout.alter_legend(fig, title='Possible SLA improvement')
    update_figs_layout.prettify_fig(fig)
    return fig