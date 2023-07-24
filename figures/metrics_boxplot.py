import plotly.graph_objects as go
import numpy as np
import datetime
def metrics_boxplot(data):
    fig = go.Figure()
    fig.add_trace(go.Box(x=data['date(dsl.created_at)'], y=data['sla_mean'], boxmean='sd', marker=dict(color='#4FFF64')))
    fig.update_yaxes(title=dict(text='Average SLA %', font=dict(size=16, family='roboto')))
    fig.update_layout(font=dict(family='roboto'), title=dict(text='SLA metrics over the last 30 days', x=0.5, y=0.93, xanchor='center', yanchor='top',
                                                             font=dict(family='roboto', size=26)), height=500,
                    )
    
    fig.update_xaxes(tickfont=dict(size=16, family='roboto'), rangeslider_visible=True, range=[np.min(data['date(dsl.created_at)'] + datetime.timedelta(days=20)),
                                                                                               np.max(data['date(dsl.created_at)']) + datetime.timedelta(days=1)])
    fig.update_yaxes(title=None, tickfont=dict(family='roboto', size=14), ticksuffix='%')
    # go.layout.XAxis.autorange()

    return fig