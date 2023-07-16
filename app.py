import streamlit as st
import plotly.express as px
import pandas as pd
from grids_sheets import GridBuilder
from figures import sla_maps
from filters import Filters
import make_circles
from shapely.geometry import Point, Polygon
import read_data

st.set_page_config(layout='wide', page_title='mapas')

def analise_descritiva(data):
    fig = px.bar(data, x='metricas', y='IEF', color='metricas', color_discrete_sequence=px.colors.qualitative.Alphabet, text_auto=True)
    fig.update_layout(title=dict(text='Análise descritiva do SLA dos dados', xanchor='center', yanchor='top', x=0.5, y=0.98, font=dict(size=25, color='whitesmoke')),
                      font=dict(family='roboto'), uniformtext_minsize=20)
    fig.update_traces(textposition='outside')
    fig.update_xaxes(title=dict(text='Métricas', font=dict(size=18, family='roboto')), showticklabels=True, tickfont=dict(size=16, family='roboto'))
    fig.update_yaxes(title=dict(text='SLA', font=dict(size=18, family='roboto')), showticklabels=True, tickfont=dict(size=16, family='roboto'))
    return fig

def start_app():
    data = read_data.read_data('projeto_comgas.csv', sep=';')
    jardins_coordenadas = read_data.read_data('coordenadas_jardins.csv')
    cp_data = data.copy()
    cp_data['Ponto'] = list(zip(cp_data['Latitude'], cp_data['Longitude']))
    cp_data['Ponto'] = cp_data['Ponto'].apply(lambda x: Point(x))

    agrupado_por_condo = data.groupby(by=['Unidade de Negócio - Nome','Cidade - Nome', 'Grupo - Nome']).agg({'IEF':'mean', 'Matrícula':'count', 'Latitude':'mean', 'Longitude':'mean'}).reset_index()
    grid_pontos_agrupados = GridBuilder(agrupado_por_condo, key='grid_pontos_agrupados')
    
    st.subheader('Pontos agrupados por condomínio')
    tabela_agrupado, dados_agrupado = grid_pontos_agrupados.grid_builder()
    filtered_group = Filters(dados_agrupado)
    filtered_data = Filters(data)

    c_BU, c_condo, c_cidade = st.columns(3)
    filtro_BU = c_BU.multiselect('Filtro de unidade de negócio', options=filtered_group.df['Unidade de Negócio - Nome'].unique())
    filtered_group.validate_filter('general_filter', filtro_BU, refer_column='Unidade de Negócio - Nome')
    filtro_condo = c_condo.multiselect('Filtro de condomínio', options=filtered_group.df['Grupo - Nome'].unique())
    filtered_group.validate_filter('general_filter', filtro_condo, refer_column='Grupo - Nome')
    filtro_cidade = c_cidade.multiselect('Filtro de cidade', options=filtered_group.df['Cidade - Nome'].unique())
    filtered_group.validate_filter('general_filter', filtro_cidade, refer_column='Cidade - Nome')

    c_num_min, c_num_max = st.columns(2)
    min_pontos = c_num_min.number_input('Número mínimo de pontos:', min_value=int(filtered_group.df['Matrícula'].min()) - 1, max_value=int(filtered_group.df['Matrícula'].max()), value=int(filtered_group.df['Matrícula'].min()) - 1)
    max_pontos = c_num_max.number_input('Número máximo de pontos:', min_value=int(filtered_group.df['Matrícula'].min()) - 1, max_value=int(filtered_group.df['Matrícula'].max()), value=int(filtered_group.df['Matrícula'].max()))
    min_sla_condo, max_sla_condo = c_num_min.slider('SLA por condomínio', min_value=0.0, max_value=100.0, value=[float(filtered_group.df.IEF.min()),float(filtered_group.df.IEF.max())], step=5.0)
    min_sla_pontos, max_sla_pontos = c_num_max.slider('SLA por instalação', min_value=0.0, max_value=100.0, value=[float(filtered_data.df.IEF.min()),float(filtered_data.df.IEF.max())], step=5.0, key='sla_slider_pontos')
   
    filtered_group.df = filtered_group.df[(filtered_group.df['Matrícula'] >= min_pontos) &
                                (filtered_group.df['Matrícula'] <= max_pontos) &
                                (filtered_group.df['IEF'] >= min_sla_condo) & (filtered_group.df['IEF'] <= max_sla_condo)]

    filtered_data.general_filter(refer_column='Unidade de Negócio - Nome', opcs=filtered_group.df['Unidade de Negócio - Nome'])
    filtered_data.general_filter(refer_column='Grupo - Nome', opcs=filtered_group.df['Grupo - Nome'])
    filtered_data.general_filter(refer_column='Cidade - Nome', opcs=filtered_group.df['Cidade - Nome'])
    filtered_data.general_qty_filter(min_sla_pontos, max_sla_pontos, 'IEF')
    

    with st.expander('Dados filtrados:'):
        filtered_group.df.rename(columns={'Matrícula':'Pontos instalados'}, inplace=True)
        st.write(filtered_group.df.sort_values(by='Pontos instalados', ascending=False))
        st.markdown('---')
        st.write(filtered_data.df.sort_values('IEF', ascending=False))

    theme_position, ponto_filtrado, *_, opc_agrupamento = st.columns(5)
    theme_position.metric('Endereços filtrados:', f'{filtered_group.df.shape[0]} ({round(filtered_group.df.shape[0] / len(agrupado_por_condo) * 100, 2)})%',
                        help=f'Total de endereços: {len(agrupado_por_condo)}')
    ponto_filtrado.metric('Pontos filtrados:', f'{filtered_data.df.shape[0]} ({round(len(filtered_data.df) / cp_data.shape[0] * 100, 2)})%',
                        help=f'Total de pontos: {cp_data.shape[0]}')

    theme_options = ['carto-darkmatter','satellite', 'satellite-streets', 'carto-positron', 'dark', 'open-street-map', 'streets', 'stamen-terrain', 'stamen-toner',
                            'stamen-watercolor', 'basic', 'outdoors', 'light', 'white-bg']

    choosed_theme = theme_position.selectbox('Choose any theme', options=theme_options, index=0)
    st.markdown('---')

    mapa_todos = sla_maps.plot_sla_map(filtered_data.df, title='Mapa de SLA teste', colmn_to_base_color='IEF', theme=choosed_theme, group_type='IEF')
    sla_maps.add_traces_on_map(mapa_todos, another_data=jardins_coordenadas, name='Área dos Jardins')
    agrupamento = opc_agrupamento.radio('Ver por:', options=['IEF', 'Pontos instalados'])
    mapa_agrupado = sla_maps.plot_sla_map(filtered_group.df, title=f'Mapa de {agrupamento} agrupado por condomínio', theme=choosed_theme, group_type=agrupamento,
                                        colmn_to_base_color=agrupamento)
    sla_maps.add_traces_on_map(mapa_agrupado, another_data=jardins_coordenadas, name='Área dos Jardins')

    metricas = filtered_group.df.describe().drop('count', axis=0).reset_index().rename(columns={'index':'metricas'})
    metricas['IEF'] = metricas['IEF'].apply(lambda x: round(x, 2))
    fig_descritiva = analise_descritiva(metricas)
    st.plotly_chart(fig_descritiva, use_container_width=True)

    st.markdown('---')
    st.subheader('Análise de alcance de gateways')
    gtw_number, gtw_range = st.columns(2)
    qty_of_gtw = gtw_number.number_input('Quantos gateways possuo: ', min_value=0, max_value=filtered_group.df['Pontos instalados'].max())
    add_gtws = gtw_number.multiselect('Ou selecione condomínios específicos', options=filtered_group.df['Grupo - Nome'].unique())
    persinalized_gtw = filtered_group.df[filtered_group.df['Grupo - Nome'].isin(add_gtws)]
    gtw_range = gtw_range.number_input('Qual o alcance em metros deles: ', min_value=1, value=1500)

    df_filtered_per_points = filtered_group.df.sort_values(by='Pontos instalados', ascending=False).iloc[:int(qty_of_gtw), :].reset_index()
    df_filtered_per_points = pd.concat([df_filtered_per_points, persinalized_gtw.reset_index()], ignore_index=True)
    qty_that_is_contained = 0
    list_of_poligons = []
    affected_points = pd.DataFrame()
    # função para calcular os polígonos
    # calcular os polúgonos anteriormente
    lat_list = []
    lon_list = []
    lat_list, lon_list = list(df_filtered_per_points['Latitude']), list(df_filtered_per_points['Longitude'])
    with st.spinner('Recalculando polígnos...'):
        for idx, lat in enumerate(lat_list):
            #cada condominio tem seu poligono
            new_lat_list = []
            new_lon_list = []
            lista = make_circles.make_circles(radius=gtw_range, point_numbers=100, lat=lat, long=lon_list[idx])
            # cada lista deve ser o polígono do condominio correspondente
            # lista = círculo de pontos
            poligono = Polygon(lista)
            for index, ponto in enumerate(cp_data['Ponto']):
                if poligono.contains(ponto):
                    affected_points = pd.concat([affected_points, cp_data.iloc[index:index + 1]])
                    qty_that_is_contained += 1

            for lists in lista:
                new_lat_list.append(lists[0])
                new_lon_list.append(lists[1])

            poligon_df = pd.DataFrame(data={'Latitude':new_lat_list, 'Longitude':new_lon_list})
            sla_maps.add_traces_on_map(mapa_agrupado, another_data=poligon_df, fillcolor='rgba(110, 226, 1, 0.2)', name=df_filtered_per_points.loc[idx:idx, 'Grupo - Nome'].values[0])
            sla_maps.add_traces_on_map(mapa_todos, another_data=poligon_df, fillcolor='rgba(110, 226, 1, 0.2)', name=df_filtered_per_points.loc[idx:idx, 'Grupo - Nome'].values[0])

        points_metrics, sla_metrics = st.columns(2)
    try:
        points_metrics.metric(f'Pontos afetados', value=f'{qty_that_is_contained} pontos')
        sla_metrics.metric(f'SLA dos pontos filtrados', value=round(affected_points['IEF'].mean(), 2))
    except: st.warning('No data filtered')

    with st.expander('Ver pontos e condomínios afetados'):
        st.write(affected_points)
        st.write(df_filtered_per_points)

    c_gtw_condos, c_gtw_pontos = st.columns(2)
    c_gtw_pontos.plotly_chart(mapa_todos, use_container_width=True)
    c_gtw_condos.plotly_chart(mapa_agrupado, use_container_width=True)

if __name__ == '__main__':
    with open('style.css') as style:
        st.markdown(f'<style>{style.read()}</style>', unsafe_allow_html=True)
    start_app()