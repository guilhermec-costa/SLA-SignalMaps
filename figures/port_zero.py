import plotly.graph_objects as go
from figures import update_figs_layout
import plotly.express as px

def port_zero_plot(data, x_axis, y_axis, segregate_bu=False):
    fig = go.Figure()
    
    fig.add_trace(go.Bar(x=data[x_axis], y=data[y_axis], name="Port 0 - All BU's", marker=dict(color=data[y_axis], colorscale='Viridis_r'),
                                    text=data[y_axis], textposition='outside',textfont=dict(size=16, family='roboto')))
    fig.update_layout(title=dict(text='Port 0 transmissions over the last 30 days', font=dict(size=26, family='roboto'), x=0.5, y=0.93, xanchor='center', yanchor='top'),
                            font=dict(family='roboto'), height=530, template='presentation')
    fig.update_yaxes(showticklabels=False)


    update_figs_layout.alter_hover(fig=fig, mode='x unified')
    update_figs_layout.prettify_fig(fig)
    fig.update_xaxes(tickvals=data['created_at'], tickangle=30)
    update_figs_layout.alter_legend(fig, title='Transmissions')

    return fig

