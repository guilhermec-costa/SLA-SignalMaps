import plotly.express as px

def analise_descritiva(data):
    fig = px.bar(data, x='metricas', y='IEF', color='metricas', color_discrete_sequence=px.colors.qualitative.Bold, text_auto=True)
    fig.update_layout(title=dict(text='Análise descritiva do SLA', xanchor='center', yanchor='top', x=0.5, y=0.98, font=dict(size=30, color='whitesmoke')),
                      font=dict(family='roboto'), uniformtext_minsize=26, height=580, template='plotly')
    fig.update_traces(textposition='outside', textfont_size=16)
    fig.update_xaxes(title=dict(text='Métricas', font=dict(size=18, family='roboto')), showticklabels=True, tickfont=dict(size=16, family='roboto'), showline=True, linewidth=1)
    fig.update_yaxes(title=dict(text='SLA', font=dict(size=18, family='roboto')), showticklabels=True, tickfont=dict(size=16, family='roboto'), showline=True, linewidth=1,
                     gridcolor='rgba(222, 223, 222, 0.1)')
    return fig