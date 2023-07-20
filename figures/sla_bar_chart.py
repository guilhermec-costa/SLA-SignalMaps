import plotly.express as px

def sla_bars(data, BU_xaxes, sla_yaxes):
    fig = px.bar(data_frame=data, x=BU_xaxes, y=sla_yaxes, color=BU_xaxes, color_discrete_sequence=px.colors.qualitative.G10)
    return fig