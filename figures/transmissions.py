from plotly.subplots import make_subplots
import plotly.graph_objects as go
from . import update_figs_layout
import numpy as np
import datetime
import streamlit as st

def daily_transmissions(data):
    fig = make_subplots(rows=1, cols=3, vertical_spacing=0.3, print_grid=True,
                    subplot_titles=tuple(bu for bu in data.name.unique()))
    
    col_pos, row_pos = 1, 1
    for idx, bu in enumerate(data['name'].unique()):
        showlegend:bool = True if idx == 0 else False

        filtered_data = data[data['name']==bu]

        fig.add_trace(go.Bar(x=filtered_data["snapshot_date"], y=filtered_data['qtd_transmissoes'], legendgroup=f'bu_{bu}', 
                                 marker=dict(color='#E8D04A'), name='Effective transmissions', showlegend=showlegend, text=filtered_data['qtd_transmissoes'],
                                 textposition='outside', textfont=dict(size=14, family='roboto')),
                      row=row_pos, col=col_pos)
        
        fig.add_trace(go.Scatter(x=filtered_data["snapshot_date"], y=filtered_data['qtd_transmissoes_meta'],
                                 legendgroup=f'bu_{bu}'#, legendgrouptitle_text=f'Messages',
                            ,marker=dict(color='#EA1B2A'), line=dict(width=3, color='#E84F3F'), name='Transmissions goal', showlegend=showlegend),
                row=row_pos, col=col_pos)
        
        fig.add_trace(go.Bar(x=filtered_data["snapshot_date"], y=filtered_data['pontos_ativos'], name='Active points', showlegend=showlegend,
                             marker=dict(color='#51DB91'), text=filtered_data['pontos_ativos'], textposition='outside',
                             textfont=dict(size=14, family='roboto')),
                      row=row_pos, col=col_pos)
    
        
        fig.update_xaxes(showgrid=True, griddash='solid', gridcolor='rgba(211, 211, 211, 0.2)', tickfont=dict(size=16, family='roboto'), tickangle=25,
                rangeslider_visible=True, range=[np.max(data.snapshot_date) - datetime.timedelta(days=2, hours=13),
                                                np.max(data.snapshot_date) + datetime.timedelta(days=1)])
        fig.update_yaxes(title=dict(text=None, font=dict(family='roboto', size=18)), tickfont=dict(family='roboto', size=14))

        col_pos += 1
        # col_pos += 1
        # if col_pos > 2:
        #     col_pos = 1
        #     row_pos += 1
    
    fig.update_layout(font=dict(family='roboto'), height=600, barmode='group', template='presentation',
                    legend=dict(
                            title=dict(text='Metrics', font=dict(family='roboto', size=16)),
                            font=dict(family='roboto', size=14)
                    ))
    fig.update_annotations(font=dict(family='roboto', size=22))
    update_figs_layout.alter_hover(fig=fig, mode='x unified')
    update_figs_layout.alter_legend(fig=fig, title='Metrics')

    return fig
    