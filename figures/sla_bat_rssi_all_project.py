import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from . import update_figs_layout

def metrics_all_projects(data):
    fig = make_subplots(rows=1, cols=3, shared_xaxes=True,
                        subplot_titles=(('SLA: all businnes units', 'RSSI: all business units', 'Battery voltage: all business units')))
    fig.add_trace(go.Scatter(x=data.index, y=data['sla_mean'], line=dict(color='#5E60FF', width=3), marker=dict(color='#A5A7F7'), mode='lines+markers', name='Average SLA %'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['rssi_mean'], name='Average RSSI', mode='lines+markers', marker=dict(color='#317575'),
                             line=dict(color='#66F2F2', width=3)), row=1, col=2)
    fig.add_trace(go.Scatter(x=data.index, y=data['battery_voltage_mean'], mode='lines+markers', name='Average battery voltage', 
                             line=dict(color='#51DB92', width=3), marker=dict(color='#2B754E')), row=1, col=3)

    fig.update_layout(legend=dict(y=0.7, yanchor='bottom'),
                      title=dict(text='Overview: all business units', font=dict(family='roboto', size=26), x=0.5, xanchor='center', y=0.98, yanchor='top'),
                      font=dict(family='roboto', size=16), height=580)
    
    fig.update_annotations(font=dict(family='roboto', size=18), y=1.04, yanchor='top')
    fig.update_yaxes(ticksuffix='%', row=1, col=1)
    fig.update_yaxes(ticksuffix='dB', row=1, col=2)
    fig.update_yaxes(ticksuffix='V', row=1, col=3)
    
    update_figs_layout.prettify_fig(fig)
    update_figs_layout.alter_hover(fig=fig, mode='x unified')
    update_figs_layout.alter_legend(fig=fig, title='Metrics')

    return fig
