import plotly.express as px

def analise_descritiva(data):
    fig = px.bar(data, x='metricas', y='IEF', color='metricas', color_discrete_sequence=px.colors.qualitative.Alphabet, text_auto=True)
    fig.update_layout(title=dict(text='Análise descritiva do SLA dos dados', xanchor='center', yanchor='top', x=0.5, y=0.98, font=dict(size=25, color='whitesmoke')),
                      font=dict(family='roboto'), uniformtext_minsize=20)
    fig.update_traces(textposition='outside')
    fig.update_xaxes(title=dict(text='Métricas', font=dict(size=18, family='roboto')), showticklabels=True, tickfont=dict(size=16, family='roboto'))
    fig.update_yaxes(title=dict(text='SLA', font=dict(size=18, family='roboto')), showticklabels=True, tickfont=dict(size=16, family='roboto'))
    return fig