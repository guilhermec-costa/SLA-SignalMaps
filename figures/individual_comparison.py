import plotly.graph_objects as go
import pandas as pd
from figures import update_figs_layout

def individual_com_figure(data:pd.DataFrame, start_date, end_date):
    fig = go.Figure()
    
    colors = ['#A45AED', '#4EED83']
    counter = 0
    for date in data['data snapshot'].unique():
        subset = data[data['data snapshot']==date]
        fig.add_trace(go.Bar(x=subset['IEF'], y=subset['Endereço'], name=date.strftime('%b, %d - %Y'), orientation='h', marker=dict(color=colors[counter]),
                             textposition='outside', text=subset['IEF'], texttemplate='%{text:.2f}%', textfont=dict(size=16)))
        counter += 1

    fig.update_layout(barmode='group', height=650, uniformtext_minsize=18, font=dict(family='roboto'), template='presentation',
                      title=dict(text=f'SLA comparison: {start_date} x {end_date}', font=dict(family='roboto', size=25), x=0.5, xanchor='center', y=0.95, yanchor='top'))
    fig.update_xaxes(ticksuffix='%', showgrid=True, gridwidth=1.5)
    update_figs_layout.prettify_fig(fig)
    update_figs_layout.alter_legend(fig, title='Analysis date')
    update_figs_layout.alter_hover(fig, mode='closest')
    return fig
