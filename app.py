import streamlit as st
import pandas as pd
from grids_sheets import GridBuilder
from figures import sla_maps, stastics_fig
from filters import Filters
from shapely.geometry import Point
import read_data
from polygons.polygons import calculate_polygons, check_if_pol_contains
from concurrent.futures import ThreadPoolExecutor
import numpy as np

st.set_page_config(layout='wide', page_title='mapas')
def start_app():
    data = read_data.read_data('projeto_comgas.csv', sep=';')
    jardins_coordenadas = read_data.read_data('coordenadas_jardins.csv')
    data['Ponto'] = list(zip(data['Latitude'], data['Longitude']))
    data['Ponto'] = data['Ponto'].apply(lambda x: Point(x))
    cp_data = data.copy()

    agrupado_por_condo = data.groupby(by=['Unidade de Negócio - Nome','Cidade - Nome', 'Grupo - Nome']).agg({'IEF':'mean', 'Matrícula':'count', 'Latitude':'mean', 'Longitude':'mean'}).reset_index()
    agrupado_por_condo.IEF = agrupado_por_condo.IEF.apply(lambda x: round(x, 2))
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

    theme_position, ponto_filtrado, sla_filtrado, opc_agrupamento, *_ = st.columns(5)
    theme_position.metric('Endereços filtrados:', f'{filtered_group.df.shape[0]} ({round(filtered_group.df.shape[0] / len(agrupado_por_condo) * 100, 2)})%',
                        help=f'Total de endereços: {len(agrupado_por_condo)}')
    ponto_filtrado.metric('Pontos filtrados:', f'{filtered_data.df.shape[0]} ({round(len(filtered_data.df) / cp_data.shape[0] * 100, 2)})%',
                        help=f'Total de pontos: {cp_data.shape[0]}')
    sla_filtrado.metric('SLA filtrado', value=f'{round(np.mean(filtered_group.df.IEF), 2)}%')
    

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
    fig_descritiva = stastics_fig.analise_descritiva(metricas)
    st.plotly_chart(fig_descritiva, use_container_width=True)

    st.markdown('---')
    st.subheader('Análise de alcance de gateways')
    gtw_number, gtw_range = st.columns(2)
    qty_of_gtw = gtw_number.number_input('Quantos gateways possuo: ', min_value=0, max_value=filtered_group.df['Pontos instalados'].max())
    add_gtws = gtw_number.multiselect('Ou selecione condomínios específicos', options=filtered_group.df['Grupo - Nome'].unique())
    personalized_gtw = filtered_group.df[filtered_group.df['Grupo - Nome'].isin(add_gtws)]
    gtw_range = gtw_range.number_input('Qual o alcance em metros deles: ', min_value=1, value=1500)

    df_filtered_per_points = filtered_group.df.sort_values(by='Pontos instalados', ascending=False).iloc[:int(qty_of_gtw), :].reset_index()
    df_filtered_per_points = pd.concat([df_filtered_per_points, personalized_gtw.reset_index()], ignore_index=True)
    qty_that_is_contained = 0
    affected_points = pd.DataFrame()

    lat_list, lon_list = list(df_filtered_per_points['Latitude']), list(df_filtered_per_points['Longitude'])
    with st.spinner('Calculando polígonos...'):
        with ThreadPoolExecutor() as executor:
            list_of_polygons = list(executor.map(calculate_polygons, lat_list, lon_list))
    
    contained_index = []
    with st.spinner('Calculando pontos  inclusos'):
        with ThreadPoolExecutor() as executor:
            for idx, lat in enumerate(lat_list):
                current_polygon, current_list_of_circles = list_of_polygons[idx][0], list_of_polygons[idx][1]
                temporary_lats = []
                temporary_longs = []
                args = [(index, ponto, current_polygon) for index, ponto in enumerate(filtered_data.df['Ponto'])]
                results = executor.map(check_if_pol_contains, args)
                contained_index.extend([i for i in results if i is not None])
                filtered_data.df = filtered_data.df[~filtered_data.df.index.isin(contained_index)]
                filtered_data.df.reset_index(inplace=True)

                for tuple_of_coord in current_list_of_circles:
                    temporary_lats.append(tuple_of_coord[0])
                    temporary_longs.append(tuple_of_coord[1])

                poligon_df = pd.DataFrame(data={'Latitude':temporary_lats, 'Longitude':temporary_longs})
                sla_maps.add_traces_on_map(mapa_agrupado, another_data=poligon_df, fillcolor='rgba(110, 226, 1, 0.2)', name=df_filtered_per_points.loc[idx:idx, 'Grupo - Nome'].values[0])
                sla_maps.add_traces_on_map(mapa_todos, another_data=poligon_df, fillcolor='rgba(110, 226, 1, 0.2)', name=df_filtered_per_points.loc[idx:idx, 'Grupo - Nome'].values[0])

    affected_points = cp_data.iloc[contained_index]
    affected_points.drop_duplicates(subset=['Matrícula'], inplace=True)
    qty_that_is_contained = affected_points.shape[0]
    points_metrics, sla_metrics = st.columns(2)
    if df_filtered_per_points.shape[0] >= 1:
        points_metrics.metric(f'Pontos afetados', value=f'{qty_that_is_contained} pontos')
        sla_metrics.metric(f'SLA dos pontos filtrados', value=round(affected_points['IEF'].mean(), 2))

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