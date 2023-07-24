import streamlit as st
import pandas as pd
from figures import sla_maps, stastics_fig, update_figs_layout, sla_indicator_chart, \
sla_last_30days, rssi_last_30days, metrics_boxplot, battery_voltage_last30days
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
        sla_data_30days = pd.DataFrame(results.get('SLA_OVER_TIME_ALL_UNITS'))
        st.header('SLA metrics')
        st.markdown('###')
        gauge_chart = sla_indicator_chart.gauge_sla_figure(df_sla_all_BU)
        sla_30days = sla_last_30days.sla_last_30days(sla_data_30days)
        rssi_30days = rssi_last_30days.rssi_last_30days(sla_data_30days)
        boxplot_metrics = metrics_boxplot.metrics_boxplot(sla_data_30days)
        battery_voltage30days = battery_voltage_last30days.battery_voltage(sla_data_30days)
        st.plotly_chart(gauge_chart, use_container_width=True)
        st.markdown('---')
        st.header('Time Series Analysis')
        st.markdown('###')
        sla_c, rssi_c = st.columns(2)
        sla_c.plotly_chart(sla_30days, use_container_width=True)
        rssi_c.plotly_chart(rssi_30days, use_container_width=True)
        st.markdown('###')
        st.markdown('###')
        sla_c.plotly_chart(boxplot_metrics, use_container_width=True)
        rssi_c.plotly_chart(battery_voltage30days, use_container_width=True)

    jardins_coordenadas = read_data.read_data('coordenadas_jardins.csv')
    df_all_unit_services['Ponto'] = list(zip(df_all_unit_services['Latitude'], df_all_unit_services['Longitude']))
    df_all_unit_services['Ponto'] = df_all_unit_services['Ponto'].apply(lambda x: Point(x))
    cp_data = df_all_unit_services.copy()

    agrupado_por_condo = df_all_unit_services.groupby(by=['Unidade de Negócio - Nome','Cidade - Nome', 'Grupo - Nome']).agg({'IEF':'mean', 'Matrícula':'count', 'Latitude':'mean', 'Longitude':'mean'}).reset_index()
    agrupado_por_condo.IEF = agrupado_por_condo.IEF.apply(lambda x: round(x, 2))
    
    st.markdown('---')
    st.subheader('Filters')
    filtered_group = Filters(agrupado_por_condo)
    filtered_data = Filters(df_all_unit_services)

    c_BU, c_condo, c_cidade = st.columns(3)
    filtro_BU = c_BU.multiselect('Business Unit', options=filtered_group.df['Unidade de Negócio - Nome'].unique())
    filtered_group.validate_filter('general_filter', filtro_BU, refer_column='Unidade de Negócio - Nome')
    filtro_condo = c_condo.multiselect('Residence name', options=filtered_group.df['Grupo - Nome'].unique())
    filtered_group.validate_filter('general_filter', filtro_condo, refer_column='Grupo - Nome')
    filtro_cidade = c_cidade.multiselect('City', options=filtered_group.df['Cidade - Nome'].unique())
    filtered_group.validate_filter('general_filter', filtro_cidade, refer_column='Cidade - Nome')

    c_num_min, c_num_max = st.columns(2)
    min_pontos = c_num_min.number_input('Min number of installations:', min_value=int(filtered_group.df['Matrícula'].min()) - 1, max_value=int(filtered_group.df['Matrícula'].max()), value=int(filtered_group.df['Matrícula'].min()) - 1)
    max_pontos = c_num_max.number_input('Max number of installations:', min_value=int(filtered_group.df['Matrícula'].min()) - 1, max_value=int(filtered_group.df['Matrícula'].max()), value=int(filtered_group.df['Matrícula'].max()))
    min_sla_condo, max_sla_condo = c_num_min.slider('SLA por condomínio', min_value=0.0, max_value=100.0, value=[float(filtered_group.df.IEF.min()),float(filtered_group.df.IEF.max())], step=5.0)
    min_sla_pontos, max_sla_pontos = c_num_max.slider('SLA por instalação', min_value=0.0, max_value=100.0, value=[float(filtered_data.df.IEF.min()),float(filtered_data.df.IEF.max())], step=5.0, key='sla_slider_pontos')
   
    filtered_group.df = filtered_group.df[(filtered_group.df['Matrícula'] >= min_pontos) &
                                (filtered_group.df['Matrícula'] <= max_pontos) &
                                (filtered_group.df['IEF'] >= min_sla_condo) & (filtered_group.df['IEF'] <= max_sla_condo)]

    filtered_data.general_filter(refer_column='Unidade de Negócio - Nome', opcs=filtered_group.df['Unidade de Negócio - Nome'])
    filtered_data.general_filter(refer_column='Grupo - Nome', opcs=filtered_group.df['Grupo - Nome'])
    filtered_data.general_filter(refer_column='Cidade - Nome', opcs=filtered_group.df['Cidade - Nome'])
    filtered_data.general_qty_filter(min_sla_pontos, max_sla_pontos, 'IEF')
    
    filtered_data_p__metrics = filtered_data.df.groupby(['data snapshot', 'Unidade de Negócio - Nome']).agg({'IEF':'mean'})
    with st.expander('Filtered data:'):
        filtered_group.df.rename(columns={'Matrícula':'Pontos instalados'}, inplace=True)
        st.write(filtered_group.df.sort_values(by='Pontos instalados', ascending=False))
        filtered_data.df.sort_values(by='IEF', ascending=False, inplace=True)
        st.markdown('---')
        st.data_editor(filtered_data.df,
                column_config={
                    "IEF":st.column_config.ProgressColumn('SLA', min_value=0, max_value=100, format='%.2f')
                })

    theme_position, ponto_filtrado, sla_filtrado, opc_agrupamento, *_ = st.columns(5)
    theme_position.metric('Filtered addresses:', f'{filtered_group.df.shape[0]} ({round(filtered_group.df.shape[0] / len(agrupado_por_condo) * 100, 2)})%',
                        help=f'Total of addresses: {len(agrupado_por_condo)}')
    ponto_filtrado.metric('Pontos filtrados:', f'{filtered_data.df.shape[0]} ({round(len(filtered_data.df) / cp_data.shape[0] * 100, 2)})%',
                        help=f'Total of installations: {cp_data.shape[0]}')
    sla_filtrado.metric('Filtered SLA %', value=f'{round(np.mean(filtered_group.df.IEF), 2)}%')
    st.markdown('---')

    st.session_state.grafico_vazio = sla_maps.plot_sla_map(filtered_data.df, title='SLA % per installation', colmn_to_base_color='IEF', theme='streets', group_type='IEF')
    sla_maps.add_traces_on_map(st.session_state.grafico_vazio, another_data=jardins_coordenadas, name='Jardins Area', fillcolor='rgba(31, 54, 251, 0.3)')
    mapa_agrupado_por_ponto = sla_maps.plot_sla_map(filtered_group.df, title=f'Installations per address', theme='streets', group_type='Pontos instalados',
                                        colmn_to_base_color='Pontos instalados')
    mapa_agrupado_por_sla = sla_maps.plot_sla_map(filtered_group.df, title=f'SLA % mean grouped per address', theme='streets', group_type='IEF',
                                        colmn_to_base_color='IEF')
    sla_maps.add_traces_on_map(mapa_agrupado_por_ponto, another_data=jardins_coordenadas, name='Jardins Area', fillcolor='rgba(31, 54, 251, 0.3)')
    sla_maps.add_traces_on_map(mapa_agrupado_por_sla, another_data=jardins_coordenadas, name='Jardins Area', fillcolor='rgba(31, 54, 251, 0.3)')

    metricas = filtered_group.df.describe().drop('count', axis=0).reset_index().rename(columns={'index':'metricas'})
    metricas['IEF'] = metricas['IEF'].apply(lambda x: round(x, 2))
    fig_descritiva = stastics_fig.analise_descritiva(metricas)
    st.plotly_chart(fig_descritiva, use_container_width=True)

    qty_that_is_contained = 0
    st.markdown('---')
    st.subheader('Gateways analysis')
    with st.expander('Edit gateway options'):
        with st.form('gtw_form'):
            gtw_number, gtw_range = st.columns(2)
            qty_of_gtw = gtw_number.number_input('Distribute some gateways: ', min_value=0, max_value=filtered_group.df['Pontos instalados'].max())
            st.session_state.extra_selected_condo = gtw_number.multiselect('Or choose any address', options=filtered_group.df['Grupo - Nome'].unique())
            personalized_gtw = filtered_group.df[filtered_group.df['Grupo - Nome'].isin(st.session_state.extra_selected_condo)]
            gtw_range = gtw_range.number_input('Gateway range in meters: ', min_value=1, value=1500)

            df_filtered_per_points = filtered_group.df.sort_values(by='Pontos instalados', ascending=False).iloc[:int(qty_of_gtw), :].reset_index()
            df_filtered_per_points = pd.concat([df_filtered_per_points, personalized_gtw.reset_index()], ignore_index=True)
            df_filtered_per_points.drop_duplicates(subset='Grupo - Nome', inplace=True, ignore_index=True)
            submit_gtw = st.form_submit_button('Start calculations')
            if submit_gtw: st.session_state.gtw_filters = True
    if st.session_state.gtw_filters:
        st.session_state.gtw_filters = False
        lat_list, lon_list = df_filtered_per_points['Latitude'].to_numpy(), df_filtered_per_points['Longitude'].to_numpy()
        with st.spinner('Calculate polygons...'):
            with ThreadPoolExecutor(4) as executor:
                list_of_polygons = list(executor.map(calculate_polygons, lat_list, lon_list, [gtw_range]*len(lat_list)))
        
        contained_index = []
        with st.spinner('Calculating polygons...'):
            with ThreadPoolExecutor(4) as executor:
                for n in stqdm(range(len(lat_list))):
                    current_polygon, current_list_of_circles = list_of_polygons[n][0], list_of_polygons[n][1]
                    args = [(index, row[-1], current_polygon) for index, *row in filtered_data.df.itertuples()]
                    results = executor.map(check_if_pol_contains, args)
                    contained_index.extend([i for i in results if i is not None])
                    filtered_data.df = filtered_data.df[~filtered_data.df.index.isin(contained_index)]

                    temporary_lats = [tuple_of_coords[0] for tuple_of_coords in current_list_of_circles]
                    temporary_longs = [tuple_of_coords[1] for tuple_of_coords in current_list_of_circles]

                    poligon_df = pd.DataFrame(data={'Latitude':temporary_lats, 'Longitude':temporary_longs})
                    sla_maps.add_traces_on_map(mapa_agrupado_por_ponto, another_data=poligon_df, fillcolor='rgba(100, 220, 245, 0.2)', name=df_filtered_per_points.loc[n:n, 'Grupo - Nome'].values[0])
                    sla_maps.add_traces_on_map(mapa_agrupado_por_sla, another_data=poligon_df, fillcolor='rgba(100, 220, 245, 0.2)', name=df_filtered_per_points.loc[n:n, 'Grupo - Nome'].values[0])                 
                    sla_maps.add_traces_on_map(st.session_state.grafico_vazio, another_data=poligon_df, fillcolor='rgba(100, 220, 245, 0.2)', name=df_filtered_per_points.loc[n:n, 'Grupo - Nome'].values[0])
        
        affected_points = cp_data.loc[contained_index]
        qty_that_is_contained = affected_points.shape[0]
        points_metrics, sla_metrics, sla_prevision = st.columns(3)
        if df_filtered_per_points.shape[0] >= 1:
            mean_sla_affecteds = round(affected_points['IEF'].mean(), 2)
            points_metrics.metric(f'Affected points', value=f'{qty_that_is_contained} pontos')
            sla_metrics.metric(f'Filtered SLA %', value=mean_sla_affecteds)
            sla_prevision.metric('Improvement preview over the general SLA %', value=f'{round(qty_that_is_contained / cp_data.shape[0] * 100, 2)}%')

            with st.expander('Addresses and installations affected'):
                st.write(affected_points)
                st.write(agrupado_por_condo[agrupado_por_condo['Grupo - Nome'].isin(affected_points['Grupo - Nome'].unique())])

    theme_position, *_ = st.columns(5)
    theme_options = ['streets', 'open-street-map', 'satellite', 'satellite-streets', 'carto-positron', 'carto-darkmatter', 'dark', 'stamen-terrain', 'stamen-toner',
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
            with st.spinner('Running queries...'):
                # with ThreadPoolExecutor(max_workers=4) as executor:
                #     st.session_state.ALL_RESULTS = list(executor.map(queries_instancy.run_queries, [queries_instancy.all_queries_commands]))
                st.session_state.ALL_RESULTS = queries_instancy.run_queries(queries_instancy.all_queries_commands)
        st.success('Connection succeded!')
        start_app(results=st.session_state.ALL_RESULTS)