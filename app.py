import streamlit as st
import plotly.express as px
import pandas as pd
from grids_sheets import GridBuilder
<<<<<<< HEAD
import plotly.graph_objects as go
=======
>>>>>>> 1f121eff6bfbe26d05c84f0a1830b655cee7940d

st.set_page_config(layout='wide', page_title='mapas')

streamlit_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');

    html, body, [class*="css"]  {
    font-family: 'Roboto', sans-serif;
    }
    </style>
"""

metric_style = """
<style>
color: red;
</style>
"""

def plot_map(data, data2, color, title, theme, tipo_de_agrupamento=None, max_size=20):
    if tipo_de_agrupamento == 'Pontos instalados':
        max_size = 45
    fig = px.scatter_mapbox(data, lat='Latitude', lon='Longitude', color=color, color_continuous_scale=px.colors.sequential.Viridis, height=750,
                            size=color, size_max=max_size, center=dict(lat=-23.5607, lon=-46.8171), zoom=8, opacity=0.95, hover_name='Grupo - Nome')
    fig.add_trace(go.Scattermapbox(lat=data2['Latitude'], lon=data2['Longitude'], mode='lines', line=dict(color='rgba(255, 0, 0, 0.1)'), fill='toself'))
    fig.update_layout(title=dict(text=title, xanchor='center', yanchor='top', x=0.5, y=0.98, font=dict(size=25, color='whitesmoke')),
                      font=dict(family='roboto'), mapbox=dict(accesstoken='pk.eyJ1IjoiY2hpbmluaGEiLCJhIjoiY2xncGdxYzByMHphNzN0bHVzN20xbjlkYyJ9.N1T4HtNFTI-kf-XQAEJNOg',
                                                              style=theme))
    return fig

def analise_descritiva(data):
    fig = px.bar(data, x='metricas', y='IEF', color='metricas', color_discrete_sequence=px.colors.qualitative.Alphabet, text_auto=True)
    fig.update_layout(title=dict(text='Análise descritiva dos dados', xanchor='center', yanchor='top', x=0.5, y=0.98, font=dict(size=25, color='whitesmoke')),
                      font=dict(family='roboto'), uniformtext_minsize=20)
    fig.update_traces(textposition='outside')
    fig.update_xaxes(title=dict(text='Métricas', font=dict(size=18, family='roboto')), showticklabels=True, tickfont=dict(size=16, family='roboto'))
    fig.update_yaxes(title=dict(text='SLA', font=dict(size=18, family='roboto')), showticklabels=True, tickfont=dict(size=16, family='roboto'))
    return fig

def plot_map_go(data, data2, title, theme):
    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(lat=data['Latitude'], lon=data['Longitude'], marker=dict(color=data['']), fill='red'))
    fig.add_trace(go.Scattermapbox(lat=data2['Latitude'], lon=data2['Longitude'], mode='lines', line=dict(color='red')))
    fig.update_layout(title=dict(text=title, xanchor='center', yanchor='top', x=0.5, y=0.98, font=dict(size=25, color='whitesmoke')),
                    font=dict(family='roboto'), mapbox=dict(accesstoken='pk.eyJ1IjoiY2hpbmluaGEiLCJhIjoiY2xncGdxYzByMHphNzN0bHVzN20xbjlkYyJ9.N1T4HtNFTI-kf-XQAEJNOg',
                                                            style=theme), height=900)
    return fig

df_lat_long = pd.DataFrame(data={'lat':[23.804, 23.6632, 23.3282, 23.507, 23.5584],
                                 'long':[-46.5265, -46.671, -46.6837, -46.5049, -46.4526]})

data = pd.read_csv('cp_todos_projetos_comgas.csv', sep=';')
lats_longs = pd.read_csv('lat_long_jardins\Jardins.csv', sep=',')
jardins_coordenadas = pd.read_csv('apenas_jardins_coordenadas.csv')
cp_data = data.copy()
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
min_pontos = c_num_min.number_input('Número mínimo de pontos:', min_value=int(dados_agrupado['Matrícula'].min()) - 1, max_value=int(dados_agrupado['Matrícula'].max()), value=int(dados_agrupado['Matrícula'].min()) - 1)
max_pontos = c_num_max.number_input('Número máximo de pontos:', min_value=int(dados_agrupado['Matrícula'].min()) - 1, max_value=int(dados_agrupado['Matrícula'].max()), value=int(dados_agrupado['Matrícula'].max()))
min_sla_condo, max_sla_condo = c_num_min.slider('SLA por condomínio', min_value=0.0, max_value=100.0, value=[float(dados_agrupado.IEF.min()),float(dados_agrupado.IEF.max())], step=5.0)
min_sla_pontos, max_sla_pontos = c_num_max.slider('SLA por instalação', min_value=0.0, max_value=100.0, value=[float(data.IEF.min()),float(data.IEF.max())], step=5.0, key='sla_slider_pontos')
dados_agrupado = dados_agrupado[(dados_agrupado['Matrícula'] >= min_pontos) &
                                (dados_agrupado['Matrícula'] <= max_pontos) & (dados_agrupado['IEF'] >= min_sla_condo) & (dados_agrupado['IEF'] <= max_sla_condo)]

data = data[data['Unidade de Negócio - Nome'].isin(dados_agrupado['Unidade de Negócio - Nome'])]
data = data[data['Grupo - Nome'].isin(dados_agrupado['Grupo - Nome'])]
data = data[data['Cidade - Nome'].isin(dados_agrupado['Cidade - Nome'])]
data = data[(data['IEF'] >= min_sla_pontos) & (data['IEF'] <=  max_sla_pontos)]
with st.expander('Dados filtrados:'):
    dados_agrupado.rename(columns={'Matrícula':'Pontos instalados'}, inplace=True)
    st.write(dados_agrupado.sort_values(by='Pontos instalados', ascending=False))
    st.markdown('---')
    st.write(data.sort_values('IEF', ascending=False))

theme_position, ponto_filtrado, *_, opc_agrupamento = st.columns(5)
theme_position.metric('Endereços filtrados:', f'{dados_agrupado.shape[0]} ({round(dados_agrupado.shape[0] / len(agrupado_por_condo) * 100, 2)})%',
                      help=f'Total de endereços: {len(agrupado_por_condo)}')
ponto_filtrado.metric('Pontos filtrados:', f'{data.shape[0]} ({round(len(data) / cp_data.shape[0] * 100, 2)})%',
                      help=f'Total de pontos: {cp_data.shape[0]}')
theme_options = ['carto-darkmatter','satellite', 'satellite-streets', 'carto-positron', 'dark', 'open-street-map', 'streets', 'stamen-terrain', 'stamen-toner',
                        'stamen-watercolor', 'basic', 'outdoors', 'light', 'white-bg']
choosed_theme = theme_position.selectbox('Choose any theme', options=theme_options, index=0)
st.markdown('---')
mapa_todos = plot_map(data=data, data2=jardins_coordenadas,color='IEF', title='Mapa de SLA: todos os pontos instalados', theme=choosed_theme)
agrupamento = opc_agrupamento.radio('Ver por:', options=['IEF', 'Pontos instalados'])
mapa_agrupado = plot_map(data=dados_agrupado, data2=jardins_coordenadas,color=agrupamento, title=f'Mapa de {agrupamento} agrupado por condomínio', theme=choosed_theme, tipo_de_agrupamento=agrupamento)
# mapa_teste = plot_map_go(dados_agrupado, data2=jardins_coordenadas,title='Scattermapbox', theme=choosed_theme)
c_todos_pontos_df, c_agrupado_df = st.columns(2)
c_todos_pontos_df.plotly_chart(mapa_todos, use_container_width=True)
c_agrupado_df.plotly_chart(mapa_agrupado, use_container_width=True)

st.markdown(streamlit_style, unsafe_allow_html=True)
<<<<<<< HEAD
metricas = dados_agrupado.describe().drop('count', axis=0).reset_index().rename(columns={'index':'metricas'})
metricas['IEF'] = metricas['IEF'].apply(lambda x: round(x, 2))
fig_descritiva = analise_descritiva(metricas)
# st.plotly_chart(fig_descritiva, use_container_width=True)
# st.plotly_chart(mapa_teste, use_container_width=True)
=======
>>>>>>> 1f121eff6bfbe26d05c84f0a1830b655cee7940d
