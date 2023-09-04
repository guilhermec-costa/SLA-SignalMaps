from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st
from . import update_figs_layout

@st.cache_data
def recent_reading(data):
    fig = make_subplots(rows=1, cols=3, vertical_spacing=0.4, print_grid=True,
                        subplot_titles=tuple(bu for bu in data['name'].unique()))
    
    color_list = ['#C47EF2', '#4EF2F2', '#F28A4E']
    counter=0
    col_pos, row_pos = 1, 1
    for idx, bu in enumerate(data['name'].unique()):
        showlegend:bool = True if idx == 0 else False

        filtered_data = data[data['name']==bu]

        fig.add_trace(go.Scatter(x=filtered_data['reading_date'], y=filtered_data['all_readings'], legendgroup=f'bu_{bu}', 
                                 line=dict(width=2.5, color=color_list[counter]), name='Sent messages', showlegend=showlegend),
                      row=row_pos, col=col_pos)
        # fig.add_trace(go.Scatter(x=filtered_data['reading_date'], y=filtered_data['lost_uplinks'], legendgroup=f'bu_{bu}'#, legendgrouptitle_text=f'Messages',
        #                          ,marker=dict(color='#FC5F4E'), line=dict(width=2), name='Lost messages', showlegend=showlegend),
        #               row=row_pos, col=col_pos)
    
        fig.update_xaxes(showgrid=True, griddash='solid', gridcolor='rgba(211, 211, 211, 0.2)', tickfont=dict(size=16, family='roboto'), tickangle=25)
        fig.update_yaxes(title=dict(text=None, font=dict(family='roboto', size=18)), tickfont=dict(family='roboto', size=14))
        fig.update_layout(height=650)
        col_pos += 1
        

        # col_pos += 1
        # if col_pos > 2:
        #     col_pos = 1
        #     row_pos += 1
        counter+=1
    
    fig.update_layout(font=dict(family='roboto'),
                      legend=dict(
                            title=dict(text='Metrics', font=dict(family='roboto', size=16)),
                            font=dict(family='roboto', size=14)
                      ))
    fig.update_annotations(font=dict(family='roboto', size=22))
    update_figs_layout.alter_hover(fig=fig, mode='x unified')
    update_figs_layout.alter_legend(fig=fig, title='Metrics')

    return fig
