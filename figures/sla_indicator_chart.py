import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import streamlit as st

def gauge_sla_figure(data):
    # specs: especificação dos tipos dos subplots, por LINHA
    fig = make_subplots(rows=1, cols=4,
                        specs=[[dict(type='domain') for _ in range(4)]],
                        subplot_titles=tuple(business_unit for business_unit in data['Unidade de Negócio - Nome'].unique()))
    
    for *row, business_unit in data.itertuples():
        title = row[1]
        sla = row[-1]
        col_position = row[0] + 1
        fig.add_trace(trace=go.Indicator(value=np.round(sla, decimals=2),
                                        mode='gauge+number+delta', 
                                        domain=dict(x=[0,1], y=[0,1]), name=title,
                                        delta={
                                            'reference':85,
                                            'decreasing':{'color':'red'},
                                            'font':{'size':25, 'family':'roboto'}
                                            },
                                        gauge={'axis':{'range':[None, 100], 'tickcolor':'lightgrey'},
                                               'bar': {'color':'#455FFF'},
                                               'bordercolor':'grey',
                                               'borderwidth': 1,
                                               'bgcolor':'white',
                                               'threshold': {
                                                   'line': {'color':'red', 'width':4},
                                                   'value':85, 'thickness':0.75

                                               },
                                               'steps': [
                                                   {'range':[0,35], 'color':'rgba(222, 73 60, 0.5)'},
                                                   {'range': [35, 65], 'color': 'rgba(245, 214, 78, 0.5)'},
                                                   {'range':[65, 100], 'color':'rgba(60, 222, 109, 0.5)'}
                                               ]}), row=1, col=col_position)

    fig.update_annotations(y=-0.1, font=dict(family='roboto', size=18, color='lightgrey'))
    fig.update_layout(font=dict(family='roboto', size=16, color='lightgrey'),
                      title=dict(text='SLA: todas as Unidades de Negócio', x=0.5, y=0.93, xanchor='center', yanchor='top',
                                 font=dict(size=35,)))
        
    return fig
    