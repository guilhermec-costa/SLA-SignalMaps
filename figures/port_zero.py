import plotly.graph_objects as go
from figures import update_figs_layout
import plotly.express as px

def port_zero_plot(data, x_axis, y_axis, segregate_bu=False):
    fig = go.Figure()
    
    if segregate_bu:
        color_list = ['#C47EF2', '#4EF2F2', '#F28A4E', '#DDF25A']
        counter = 0
        for bu in data['name'].unique():
            subset_data = data[data['name']==bu]
            fig.add_trace(go.Scatter(x=subset_data[x_axis], y=subset_data[y_axis], mode='lines+markers', name=bu, line=dict(width=2, color=color_list[counter]),
                                     text=subset_data[y_axis], textfont=dict(size=15, family='roboto')))
            fig.update_layout(title=dict(text='Port 0 transmissions over the last 30 days by BU', font=dict(size=26, family='roboto'), x=0.5, y=0.93, xanchor='center', yanchor='top'),
                              font=dict(family='roboto'), height=530, template='presentation')
            fig.update_yaxes(showticklabels=True)
            counter+=1
    else:
        fig.add_trace(go.Bar(x=data[x_axis], y=data[y_axis], name="Port 0 - All BU's", marker=dict(color=data[y_axis], colorscale='Viridis_r'),
                                    text=data[y_axis], textposition='outside',textfont=dict(size=15, family='roboto')))
        fig.update_layout(title=dict(text='Port 0 transmissions over the last 30 days', font=dict(size=26, family='roboto'), x=0.5, y=0.93, xanchor='center', yanchor='top'),
                            font=dict(family='roboto'), height=530, template='presentation')
        fig.update_yaxes(showticklabels=False)


    update_figs_layout.alter_hover(fig=fig, mode='x unified')
    update_figs_layout.prettify_fig(fig)
    fig.update_xaxes(tickvals=data['created_at'], tickangle=30)
    update_figs_layout.alter_legend(fig, title='Transmissions')

    return fig

