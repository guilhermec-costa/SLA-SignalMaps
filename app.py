import streamlit as st
import plotly.express as px
import pandas as pd
from grids_sheets import GridBuilder
import googlemaps

st.set_page_config(layout='wide', page_title='mapas')

streamlit_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');

    html, body, [class*="css"]  {
    font-family: 'Roboto', sans-serif;
    }
    </style>
"""

def plot_map(data, color, title, theme, max_size=20):
    fig = px.scatter_mapbox(data, lat='Latitude', lon='Longitude', color=color, color_continuous_scale=px.colors.sequential.Viridis, height=700,
                            size=color, size_max=max_size, center=dict(lat=-23.5607, lon=-46.8171), zoom=8, opacity=0.95, hover_name='Grupo - Nome')
    fig.update_layout(mapbox=dict(style=theme), title=dict(text=title, xanchor='center', yanchor='top', x=0.5, y=0.88, font=dict(size=25, color='whitesmoke')))
    return fig


data = pd.read_csv('cp_todos_projetos_comgas.csv', sep=';')
agrupado_por_condo = data.groupby(by=['Unidade de Negócio - Nome','Cidade - Nome', 'Grupo - Nome']).agg({'IEF':'mean', 'Matrícula':'count', 'Latitude':'mean', 'Longitude':'mean'}).reset_index()
grid_pontos_agrupados = GridBuilder(agrupado_por_condo, key='grid_pontos_agrupados')
 
st.subheader('Pontos agrupados por condomínio')
tabela_agrupado, dados_agrupado = grid_pontos_agrupados.grid_builder()

c_BU, c_condo, c_cidade = st.columns(3)
filtro_BU = c_BU.multiselect('Filtro de unidade de negócio', options=dados_agrupado['Unidade de Negócio - Nome'].unique())
if len(filtro_BU) >= 1:
    dados_agrupado = dados_agrupado[dados_agrupado['Unidade de Negócio - Nome'].isin(filtro_BU)]
filtro_condo = c_condo.multiselect('Filtro de condomínio', options=dados_agrupado['Grupo - Nome'].unique())
if len(filtro_condo) >= 1:
    dados_agrupado = dados_agrupado[dados_agrupado['Grupo - Nome'].isin(filtro_condo)]
filtro_cidade = c_cidade.multiselect('Filtro de cidade', options=dados_agrupado['Cidade - Nome'].unique())
if len(filtro_cidade) >= 1:
    dados_agrupado = dados_agrupado[dados_agrupado['Cidade - Nome'].isin(filtro_cidade)]


c_num_min, c_num_max = st.columns(2)
min_pontos = c_num_min.number_input('Número mínimo de pontos:', min_value=1, max_value=int(dados_agrupado['Matrícula'].max()), value=1)
max_pontos = c_num_max.number_input('Número máximo de pontos:', min_value=1, max_value=int(dados_agrupado['Matrícula'].max()), value=int(dados_agrupado['Matrícula'].max()))
min_sla, max_sla = st.slider('Slider de sla', min_value=0.0, max_value=100.0, value=[float(dados_agrupado.IEF.min()),float(dados_agrupado.IEF.max())], step=5.0)
dados_agrupado = dados_agrupado[(dados_agrupado['Matrícula'] >= min_pontos) &
                                (dados_agrupado['Matrícula'] <= max_pontos) & (dados_agrupado['IEF'] >= min_sla) & (dados_agrupado['IEF'] <= max_sla)]

data = data[data['Grupo - Nome'].isin(dados_agrupado['Grupo - Nome']) & data['Unidade de Negócio - Nome'].isin(dados_agrupado['Unidade de Negócio - Nome'])
            & (data['IEF'] >= dados_agrupado['IEF'].min()) & (data['IEF'] <= dados_agrupado['IEF'].max()) & (data['Cidade - Nome'].isin(dados_agrupado['Cidade - Nome']))]

st.header(f'Quantidade de pontos filtrados: {data.shape[0]} pontos')
theme_position, *_ = st.columns(5)
theme_options = ['satellite', 'satellite-streets', 'carto-positron', 'carto-darkmatter', 'dark', 'open-street-map', 'streets', 'stamen-terrain', 'stamen-toner',
                        'stamen-watercolor', 'basic', 'outdoors', 'light', 'white-bg']
choosed_theme = theme_position.selectbox('Choose any theme', options=theme_options, index=0)
mapa_todos = plot_map(data=data, color='IEF', title='Mapa de SLA: todos os pontos instalados', theme='carto-darkmatter')
mapa_agrupado = plot_map(data=dados_agrupado, color='IEF', title='Mapa de SLA: todos os pontos agrupados por endereço', theme='carto-darkmatter')
mapa_agrupado_instalacoes = plot_map(data=dados_agrupado, color='Matrícula', max_size=45, title='todos os pontos agrupados por endereço', theme='carto-darkmatter')
c_todos_pontos_df, c_agrupado_df = st.columns(2)
c_todos_pontos_df.subheader('Mapa de todas as instalações')
c_todos_pontos_df.plotly_chart(mapa_todos, use_container_width=True)
c_agrupado_df.subheader('Mapa de instalaçoes agrupadas por condomínio')
c_agrupado_df.plotly_chart(mapa_agrupado, use_container_width=True)
st.plotly_chart(mapa_agrupado_instalacoes, use_container_width=True)

st.markdown(streamlit_style, unsafe_allow_html=True)