import plotly.graph_objects as go
from plotly.subplots import make_subplots
from . import update_figs_layout

def sla_per_city(data):
    continuous_scale = [(0, '#F51113'),(0.5, '#F5C105'),(1, '#1DF559')]

    fig = make_subplots(rows=1, cols=2, shared_yaxes=True,
                        subplot_titles=(('SLA % per City', 'Installations per city')))
    # fig = px.bar(data, x='IEF', y=data.index, orientation='h', color='IEF', color_continuous_scale=continuous_scale,
    #              text_auto=True)

    fig.add_trace(go.Bar(x=data.IEF, y=data.index, orientation='h', marker=dict(color=data['IEF'], colorscale=continuous_scale),
                         textposition='auto', text=data['IEF']), row=1, col=1)
    fig.add_trace(go.Bar(x=data['Matrícula'], y=data.index, orientation='h', marker=dict(color=data['Matrícula'], colorscale=continuous_scale),
                         textposition='auto', text=data['Matrícula']), row=1, col=2)

    fig.update_xaxes(tickfont=dict(family='roboto', size=15), showgrid=True, gridwidth=2, ticksuffix='%',
                     title=dict(text='SLA', font=dict(size=14, family='roboto')), row=1, col=1)
    
    fig.update_xaxes(tickfont=dict(family='roboto', size=15), showgrid=True, gridwidth=2,
                     title=dict(text='Installations', font=dict(size=14, family='roboto')), row=1, col=2)
    
    fig.update_yaxes(tickfont=dict(family='roboto', size=15), title=None)
    fig.update_layout(height=650, font=dict(family='roboto', size=16), showlegend=False,
                      title=dict(text='SLA x Installations (per city)', x=0.5, y=0.97, xanchor='center', yanchor='top',
                                 font=dict(size=26, family='roboto')))
    
    fig.update_annotations(font=dict(size=18, family='roboto'))
    fig.update_traces(textposition='outside')
    update_figs_layout.alter_hover(fig=fig, mode='closest')

    return fig
