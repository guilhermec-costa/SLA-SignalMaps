import streamlit as st
import pandas as pd
from figures import sla_maps, stastics_fig, update_figs_layout, sla_bar_chart, sla_indicator_chart
from filters import Filters
from shapely.geometry import Point
import read_data
from polygons.polygons import calculate_polygons, check_if_pol_contains
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from stqdm import stqdm
from queries import querie_builder
from queries.all_queries import queries_constants

st.set_page_config(layout='wide', page_title='mapas')
def initialize_session_states():
    if 'gtw_filters' not in st.session_state:
        st.session_state.gtw_filters = False
    if 'extra_selected_condo' not in st.session_state:
        st.session_state.extra_selected_condo = []
    if 'grafico_vazio' not in st.session_state:
        st.session_state.grafico_vazio = []
    if 'ALL_RESULTS' not in st.session_state:
        st.session_state.ALL_RESULTS = None

def start_app(results):
    if not results is None:
        df_all_unit_services = pd.DataFrame(results.get('ALL_UNITS'))
        df_sla_all_BU = df_all_unit_services.groupby('Unidade de Negócio - Nome').agg({'IEF':'mean', 'Matrícula':'count'}).reset_index()
        st.data_editor(
            data=df_sla_all_BU,
            column_config={'IEF':st.column_config.ProgressColumn(min_value=0, max_value=100, label='SLA', format=f'{"%"}%.2f')},
            hide_index=True
        )
        gauge_chart = sla_indicator_chart.gauge_sla_figure(df_sla_all_BU)
        st.plotly_chart(gauge_chart, use_container_width=True)

    data = read_data.read_data('projeto_comgas.csv', sep=';')
    jardins_coordenadas = read_data.read_data('coordenadas_jardins.csv')
    df_all_unit_services['Ponto'] = list(zip(df_all_unit_services['Latitude'], df_all_unit_services['Longitude']))
    df_all_unit_services['Ponto'] = df_all_unit_services['Ponto'].apply(lambda x: Point(x))
    cp_data = df_all_unit_services.copy()

    agrupado_por_condo = df_all_unit_services.groupby(by=['Unidade de Negócio - Nome','Cidade - Nome', 'Grupo - Nome']).agg({'IEF':'mean', 'Matrícula':'count', 'Latitude':'mean', 'Longitude':'mean'}).reset_index()
    agrupado_por_condo.IEF = agrupado_por_condo.IEF.apply(lambda x: round(x, 2))
    # grid_pontos_agrupados = GridBuilder(agrupado_por_condo, key='grid_pontos_agrupados')
    
    st.markdown('---')
    st.subheader('Filtros')
    # tabela_agrupado, dados_agrupado = grid_pontos_agrupados.grid_builder()
    filtered_group = Filters(agrupado_por_condo)
    filtered_data = Filters(df_all_unit_services)

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
        st.write(filtered_data.df)

    theme_position, ponto_filtrado, sla_filtrado, opc_agrupamento, *_ = st.columns(5)
    theme_position.metric('Endereços filtrados:', f'{filtered_group.df.shape[0]} ({round(filtered_group.df.shape[0] / len(agrupado_por_condo) * 100, 2)})%',
                        help=f'Total de endereços: {len(agrupado_por_condo)}')
    ponto_filtrado.metric('Pontos filtrados:', f'{filtered_data.df.shape[0]} ({round(len(filtered_data.df) / cp_data.shape[0] * 100, 2)})%',
                        help=f'Total de pontos: {cp_data.shape[0]}')
    sla_filtrado.metric('SLA filtrado', value=f'{round(np.mean(filtered_group.df.IEF), 2)}%')
    st.markdown('---')

    st.session_state.grafico_vazio = sla_maps.plot_sla_map(filtered_data.df, title='Mapa: SLA de cada ponto', colmn_to_base_color='IEF', theme='open-street-map', group_type='IEF')
    sla_maps.add_traces_on_map(st.session_state.grafico_vazio, another_data=jardins_coordenadas, name='Área dos Jardins')
    mapa_agrupado_por_ponto = sla_maps.plot_sla_map(filtered_group.df, title=f'Mapa: Pontos instalados agrupados por condomínio', theme='open-street-map', group_type='Pontos instalados',
                                        colmn_to_base_color='Pontos instalados')
    mapa_agrupado_por_sla = sla_maps.plot_sla_map(filtered_group.df, title=f'Mapa: SLA agrupado por condomínio', theme='open-street-map', group_type='IEF',
                                        colmn_to_base_color='IEF')
    sla_maps.add_traces_on_map(mapa_agrupado_por_ponto, another_data=jardins_coordenadas, name='Área dos Jardins')
    sla_maps.add_traces_on_map(mapa_agrupado_por_sla, another_data=jardins_coordenadas, name='Área dos Jardins')

    metricas = filtered_group.df.describe().drop('count', axis=0).reset_index().rename(columns={'index':'metricas'})
    metricas['IEF'] = metricas['IEF'].apply(lambda x: round(x, 2))
    fig_descritiva = stastics_fig.analise_descritiva(metricas)
    st.plotly_chart(fig_descritiva, use_container_width=True)

    qty_that_is_contained = 0
    st.markdown('---')
    st.subheader('Análise de alcance de gateways')
    with st.expander('Editar formulário de gateway'):
        with st.form('gtw_form'):
            gtw_number, gtw_range = st.columns(2)
            qty_of_gtw = gtw_number.number_input('Distribuir gateways nos condomínios top instalações: ', min_value=0, max_value=filtered_group.df['Pontos instalados'].max())
            st.session_state.extra_selected_condo = gtw_number.multiselect('Ou selecione condomínios específicos', options=filtered_group.df['Grupo - Nome'].unique())
            personalized_gtw = filtered_group.df[filtered_group.df['Grupo - Nome'].isin(st.session_state.extra_selected_condo)]
            gtw_range = gtw_range.number_input('Qual o alcance em metros deles: ', min_value=1, value=1500)

            df_filtered_per_points = filtered_group.df.sort_values(by='Pontos instalados', ascending=False).iloc[:int(qty_of_gtw), :].reset_index()
            df_filtered_per_points = pd.concat([df_filtered_per_points, personalized_gtw.reset_index()], ignore_index=True)
            df_filtered_per_points.drop_duplicates(subset='Grupo - Nome', inplace=True, ignore_index=True)
            submit_gtw = st.form_submit_button('Submit')
            if submit_gtw: st.session_state.gtw_filters = True
    if st.session_state.gtw_filters:
        st.session_state.gtw_filters = False
        lat_list, lon_list = df_filtered_per_points['Latitude'].to_numpy(), df_filtered_per_points['Longitude'].to_numpy()
        with st.spinner('Calculando polígonos...'):
            with ThreadPoolExecutor(4) as executor:
                list_of_polygons = list(executor.map(calculate_polygons, lat_list, lon_list, [gtw_range]*len(lat_list)))
        
        contained_index = []
        with st.spinner('Calculando pontos  inclusos'):
            with ThreadPoolExecutor(4) as executor:
                for n in stqdm(range(len(lat_list))):
                # for idx, lat in enumerate(lat_list):
                    current_polygon, current_list_of_circles = list_of_polygons[n][0], list_of_polygons[n][1]
                    print('Polígono de {}'.format(df_filtered_per_points.loc[n, 'Grupo - Nome']))
                    print(current_polygon)
                    args = [(index, row[-1], current_polygon) for index, *row in filtered_data.df.itertuples()]
                    results = executor.map(check_if_pol_contains, args)
                    contained_index.extend([i for i in results if i is not None])
                    filtered_data.df = filtered_data.df[~filtered_data.df.index.isin(contained_index)]

                    temporary_lats = [tuple_of_coords[0] for tuple_of_coords in current_list_of_circles]
                    temporary_longs = [tuple_of_coords[1] for tuple_of_coords in current_list_of_circles]

                    poligon_df = pd.DataFrame(data={'Latitude':temporary_lats, 'Longitude':temporary_longs})
                    sla_maps.add_traces_on_map(mapa_agrupado_por_ponto, another_data=poligon_df, fillcolor='rgba(36, 122, 3, 0.2)', name=df_filtered_per_points.loc[n:n, 'Grupo - Nome'].values[0])
                    sla_maps.add_traces_on_map(mapa_agrupado_por_sla, another_data=poligon_df, fillcolor='rgba(36, 122, 3, 0.2)', name=df_filtered_per_points.loc[n:n, 'Grupo - Nome'].values[0])                 
                    sla_maps.add_traces_on_map(st.session_state.grafico_vazio, another_data=poligon_df, fillcolor='rgba(36, 122, 3, 0.2)', name=df_filtered_per_points.loc[n:n, 'Grupo - Nome'].values[0])
        
        affected_points = cp_data.loc[contained_index]
        qty_that_is_contained = affected_points.shape[0]
        points_metrics, sla_metrics, sla_prevision = st.columns(3)
        if df_filtered_per_points.shape[0] >= 1:
            mean_sla_affecteds = round(affected_points['IEF'].mean(), 2)
            points_metrics.metric(f'Pontos afetados', value=f'{qty_that_is_contained} pontos')
            sla_metrics.metric(f'SLA dos pontos filtrados', value=mean_sla_affecteds)
            sla_prevision.metric('Previsão de melhora no SLA geral', value=f'{round(qty_that_is_contained / cp_data.shape[0] * 100, 2)}%')

            with st.expander('Ver pontos e condomínios afetados'):
                st.write(affected_points)
                st.write(agrupado_por_condo[agrupado_por_condo['Grupo - Nome'].isin(affected_points['Grupo - Nome'].unique())])

    theme_position, *_ = st.columns(5)
    theme_options = ['open-street-map', 'satellite', 'satellite-streets', 'carto-positron', 'carto-darkmatter', 'dark', 'streets', 'stamen-terrain', 'stamen-toner',
                        'stamen-watercolor', 'basic', 'outdoors', 'light', 'white-bg']
    choosed_theme = theme_position.selectbox('Choose any theme', options=theme_options, index=0)
    update_figs_layout.update_fig_layouts([mapa_agrupado_por_ponto, mapa_agrupado_por_sla, st.session_state.grafico_vazio], theme=choosed_theme)

    c_gtw_condos, c_gtw_pontos = st.columns(2)
    c_gtw_condos.plotly_chart(mapa_agrupado_por_ponto, use_container_width=True)
    c_gtw_pontos.plotly_chart(mapa_agrupado_por_sla, use_container_width=True)
    st.plotly_chart(st.session_state.grafico_vazio, use_container_width=True)
    

if __name__ == '__main__':
    with open('style.css') as style:
        st.markdown(f'<style>{style.read()}</style>', unsafe_allow_html=True)

    initialize_session_states()
    queries_instancy = querie_builder.Queries()

    if not queries_instancy.connection is None:
        queries_instancy.add_queries(queries_constants)
        # partial_run_queries = partial(queries_instancy.run_queries, query_commands=queries_instancy.all_queries_commands)
        start_querie = st.button('Start queries', key='start_queries', type='primary')
        if start_querie:
            with st.spinner('Fazendo queries...'):
                # with ThreadPoolExecutor(max_workers=4) as executor:
                #     st.session_state.ALL_RESULTS = list(executor.map(queries_instancy.run_queries, [queries_instancy.all_queries_commands]))
                st.session_state.ALL_RESULTS = queries_instancy.run_queries(queries_instancy.all_queries_commands)
        st.success('Conexão com banco bem sucedida')
        start_app(results=st.session_state.ALL_RESULTS)