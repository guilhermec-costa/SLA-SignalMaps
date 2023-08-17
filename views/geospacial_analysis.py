# geospacial nalysis code
import streamlit as st
import datetime
from queries import querie_builder, data_treatement
from shapely import Point
from filters import Filters
from figures import individual_comparison, sla_maps, stastics_fig, update_figs_layout
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from stqdm import stqdm
from polygons import polygons
import pandas as pd
from queries import queries_raw_code
import session_states

@st.cache_data()
def tmp_coordinates(tmp_lats, tmp_longs):
    return pd.DataFrame(data={'Latitude':tmp_lats, 'Longitude':tmp_longs})
    
def geo_analysis(results: querie_builder.Queries, main_data=None):
    tmp_connection = querie_builder.Queries(name='temporary_queries')

    session_states.initialize_session_states([('gtw_filters', False), ('extra_selected_condo', []), ('extra_selected_residence', []), ('grafico_vazio', []), ('ALL_RESULTS', None),
                                              ('polygon_df', pd.DataFrame()), ('city_filter', []), ('address_filter', []), ('residence_filter', [])])
    df_all_unit_services = querie_builder.Queries.load_imporant_data(queries_responses=results, specific_response='ALL_UNITS')
    jardins_coordenadas = data_treatement.read_data('coordenadas_jardins.csv')
    df_all_unit_services['Ponto'] = list(zip(df_all_unit_services['Latitude'], df_all_unit_services['Longitude']))
    df_all_unit_services['Ponto'] = df_all_unit_services['Ponto'].apply(lambda x: Point(x))
    cp_data = df_all_unit_services.copy()

    agrupado_por_condo = df_all_unit_services.groupby(by=['Unidade de Negócio - Nome','Cidade - Nome', 'Grupo - Nome', 'Endereço']).agg({'IEF':np.mean, 'Matrícula':'count', 'Latitude':np.mean, 'Longitude':np.mean}).reset_index()
    agrupado_por_condo.IEF = agrupado_por_condo.IEF.apply(lambda x: round(x, 2))
    
    st.markdown('---')
    st.subheader('Filters')
    filtered_group = Filters(agrupado_por_condo)
    filtered_data = Filters(df_all_unit_services)

    with st.form(key='submit_sla_form'):
        c_BU, c_city = st.columns(2)
        filtro_BU = c_BU.multiselect('Business Unit', options=filtered_group.df['Unidade de Negócio - Nome'].unique(), default=filtered_group.df['Unidade de Negócio - Nome'].unique())
        st.session_state.city_filter = c_city.multiselect('City', options=filtered_group.df['Cidade - Nome'].unique(), default=filtered_group.df['Cidade - Nome'].unique())

        c_num_min, c_num_max, c_status_date = st.columns(3)


        min_pontos = c_num_min.number_input('Min number of installations:', min_value=int(filtered_group.df['Matrícula'].min()) - 1, max_value=int(filtered_group.df['Matrícula'].max()), value=int(filtered_group.df['Matrícula'].min()) - 1)
        max_pontos = c_num_max.number_input('Max number of installations:', min_value=int(filtered_group.df['Matrícula'].min()) - 1, max_value=int(filtered_group.df['Matrícula'].max()), value=int(filtered_group.df['Matrícula'].max()))

        status_date = c_status_date.date_input('Day of the status', value=datetime.datetime.today(), max_value=datetime.datetime.today())
        min_sla_condo, max_sla_condo = c_num_min.slider('SLA por condomínio', min_value=0.0, max_value=100.0, value=[float(filtered_group.df.IEF.min()),float(filtered_group.df.IEF.max())], step=5.0)
        min_sla_pontos, max_sla_pontos = c_num_max.slider('SLA por instalação', min_value=0.0, max_value=100.0, value=[float(filtered_data.df.IEF.min()),float(filtered_data.df.IEF.max())], step=5.0, key='sla_slider_pontos')
        submit_form = st.form_submit_button('Submit the form')
        if submit_form:
            new_query = queries_raw_code.all_units_info(status_date, bussiness_unts=filtro_BU, cities=st.session_state.city_filter)
            new_query_result = pd.DataFrame(tmp_connection.run_single_query(command=new_query))
            filtered_data.df = new_query_result
            filtered_data.general_qty_filter(min_sla_pontos, max_sla_pontos, 'IEF')
            filtered_data.validate_filter('general_filter', st.session_state.city_filter, refer_column='Cidade - Nome')
            agrupado_por_condo = filtered_data.df.groupby(by=['Unidade de Negócio - Nome','Cidade - Nome', 'Grupo - Nome', 'Endereço']).agg({'IEF':np.mean, 'Matrícula':'count', 'Latitude':np.mean, 'Longitude':np.mean, 'data snapshot':np.max}).reset_index()
            agrupado_por_condo.IEF = agrupado_por_condo.IEF.apply(lambda x: round(x, 2))
            filtered_group = Filters(agrupado_por_condo)
            filtered_group.validate_filter('general_filter', filtro_BU, refer_column='Unidade de Negócio - Nome')
            
    
    filtered_group.df = filtered_group.df[(filtered_group.df['Matrícula'] >= min_pontos) &
                                (filtered_group.df['Matrícula'] <= max_pontos) &
                                (filtered_group.df['IEF'] >= min_sla_condo) & (filtered_group.df['IEF'] <= max_sla_condo)]

    c_address, c_group = st.columns(2)
    st.session_state.address_filter = c_address.multiselect('Address name', options=filtered_group.df['Endereço'].unique())
    filtered_group.validate_filter('general_filter', st.session_state.address_filter, refer_column='Endereço')
    st.session_state.residence_filter = c_group.multiselect('Residence name', options=filtered_group.df['Grupo - Nome'].unique())
    filtered_group.validate_filter('general_filter', st.session_state.residence_filter, refer_column='Grupo - Nome')


    filtered_data.general_filter(refer_column='Unidade de Negócio - Nome', opcs=filtered_group.df['Unidade de Negócio - Nome'])
    filtered_data.general_filter(refer_column='Endereço', opcs=filtered_group.df['Endereço'])
    filtered_data.general_filter(refer_column='Grupo - Nome', opcs=filtered_group.df['Grupo - Nome'])
    filtered_data.general_filter(refer_column='Cidade - Nome', opcs=filtered_group.df['Cidade - Nome'])
    
    
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
    sla_filtrado.metric('Filtered SLA %', value=f'{round(np.mean(filtered_data.df.IEF), 2)}%')
    st.markdown('---')
    
    st.session_state.grafico_vazio = sla_maps.plot_sla_map(filtered_data.df, title='SLA % per installation', colmn_to_base_color='IEF', theme='streets', group_type='IEF')
    sla_maps.add_traces_on_map(st.session_state.grafico_vazio, another_data=jardins_coordenadas, name='Jardins Area', fillcolor='rgba(31, 54, 251, 0.3)')
    mapa_agrupado_por_ponto = sla_maps.plot_sla_map(filtered_group.df, title=f'Installations per address', theme='streets', group_type='Pontos instalados',
                                        colmn_to_base_color='Pontos instalados')
    mapa_agrupado_por_sla = sla_maps.plot_sla_map(filtered_group.df, title=f'SLA % mean grouped per address', theme='streets', group_type='IEF',
                                        colmn_to_base_color='IEF')
    sla_maps.add_traces_on_map(mapa_agrupado_por_ponto, another_data=jardins_coordenadas, name='Jardins Area', fillcolor='rgba(31, 54, 251, 0.3)')
    sla_maps.add_traces_on_map(mapa_agrupado_por_sla, another_data=jardins_coordenadas, name='Jardins Area', fillcolor='rgba(32, 54, 251, 0.3)')

    metricas_sla_indiv = filtered_data.df.describe().drop('count', axis=0).reset_index().rename(columns={'index':'metricas'})
    metricas_sla_indiv.IEF = metricas_sla_indiv.IEF.apply(lambda x: round(x, 2))
    fig_descritiva = stastics_fig.analise_descritiva(metricas_sla_indiv)
    st.plotly_chart(fig_descritiva, use_container_width=True)
    qty_that_is_contained = 0
    st.markdown('---')
    st.subheader('Gateways analysis')
    with st.expander('Edit gateway options'):
        with st.form('gtw_form'):
            c_gtw_number, c_gtw_range = st.columns(2)
            qty_of_gtw = c_gtw_number.number_input('Distribute some gateways: ', min_value=0, max_value=filtered_group.df['Pontos instalados'].max())
            st.session_state.extra_selected_address = c_gtw_number.multiselect('Or choose any address', options=filtered_group.df['Endereço'].unique())
            st.session_state.extra_selected_residence = c_gtw_range.multiselect('Or choose any residence name', options=filtered_group.df['Grupo - Nome'].unique())

            personalized_gtw = filtered_group.df[(filtered_group.df['Endereço'].isin(st.session_state.extra_selected_address))|(filtered_group.df['Grupo - Nome'].isin(st.session_state.extra_selected_residence))]
            gtw_range = c_gtw_range.number_input('Gateway range in meters: ', min_value=1, value=1000)


            df_filtered_per_points = filtered_group.df.sort_values(by='Pontos instalados', ascending=False).iloc[:int(qty_of_gtw), :].reset_index()
            df_filtered_per_points = pd.concat([df_filtered_per_points, personalized_gtw.reset_index()], ignore_index=True)
            df_filtered_per_points.sort_values(by='Pontos instalados', ascending=False, ignore_index=True, inplace=True)
            df_filtered_per_points.drop_duplicates(subset='Endereço', inplace=True, ignore_index=True, keep='first')
            submit_gtw = st.form_submit_button('Start calculations')
            st.subheader('Ordem de prioridade para instalação de gateways')
            st.write(df_filtered_per_points)
            if submit_gtw: st.session_state.gtw_filters = True
                            
    if st.session_state.gtw_filters:
        st.session_state.gtw_filters = False
        lat_list, lon_list = df_filtered_per_points['Latitude'].to_numpy(), df_filtered_per_points['Longitude'].to_numpy()
        with st.spinner('Calculate polygons...'):
            with ThreadPoolExecutor(4) as executor:
                list_of_polygons = list(executor.map(polygons.calculate_polygons, lat_list, lon_list, [gtw_range]*len(lat_list)))
        
        contained_index = []
        with st.spinner('Calculating polygons...'):
            with ThreadPoolExecutor(4) as executor:
                for n in stqdm(range(len(lat_list))):
                    current_polygon, current_list_of_circles = list_of_polygons[n][0], list_of_polygons[n][1]
                    args = [(index, row[-1], current_polygon) for index, *row in filtered_data.df.itertuples()]
                    results = executor.map(polygons.check_if_pol_contains, args)
                    contained_index.extend([i for i in results if i is not None])
                    filtered_data.df = filtered_data.df[~filtered_data.df.index.isin(contained_index)]

                    temporary_lats = [tuple_of_coords[0] for tuple_of_coords in current_list_of_circles]
                    temporary_longs = [tuple_of_coords[1] for tuple_of_coords in current_list_of_circles]

                    st.session_state.polygon_df = tmp_coordinates(temporary_lats, temporary_longs)
                    sla_maps.add_traces_on_map(mapa_agrupado_por_ponto, another_data=st.session_state.polygon_df, fillcolor='rgba(20, 2222, 169, 0.4)', name=df_filtered_per_points.loc[n:n, 'Endereço'].values[0])
                    sla_maps.add_traces_on_map(mapa_agrupado_por_sla, another_data=st.session_state.polygon_df, fillcolor='rgba(20, 222, 169, 0.4)', name=df_filtered_per_points.loc[n:n, 'Endereço'].values[0])                 
                    sla_maps.add_traces_on_map(st.session_state.grafico_vazio, another_data=st.session_state.polygon_df, fillcolor='rgba(20, 222, 169, 0.4)', name=df_filtered_per_points.loc[n:n, 'Endereço'].values[0])
        
        affected_points = cp_data.loc[contained_index]
        qty_that_is_contained = affected_points.shape[0]
        points_metrics, choosed_gtw_qtd, sla_metrics, sla_prevision = st.columns(4)
        
        if df_filtered_per_points.shape[0] >= 1:
            mean_sla_affecteds = round(affected_points['IEF'].mean(), 2)
            points_metrics.metric(f'Affected points', value=f'{qty_that_is_contained} pontos')
            choosed_gtw_qtd.metric('Quantity of gateways: ', value=f'{len(lat_list)} gateways')
            sla_metrics.metric(f'Filtered SLA %', value=mean_sla_affecteds)
            sla_prevision.metric('Improvement preview over the general SLA %', value=f'{round(qty_that_is_contained / cp_data.shape[0] * 100, 2)}%')

            with st.expander('Addresses and installations affected'):
                st.write(affected_points)
                st.write(agrupado_por_condo[agrupado_por_condo['Endereço'].isin(affected_points['Endereço'].unique())].sort_values(by='Matrícula', ascending=False))

    theme_position, *_ = st.columns(5)
    theme_options = ['satellite-streets', 'open-street-map', 'satellite', 'streets', 'carto-positron', 'carto-darkmatter', 'dark', 'stamen-terrain', 'stamen-toner',
                        'stamen-watercolor', 'basic', 'outdoors', 'light', 'white-bg']
    choosed_theme = theme_position.selectbox('Choose any theme', options=theme_options, index=0)
    update_figs_layout.update_fig_layouts([mapa_agrupado_por_ponto, mapa_agrupado_por_sla, st.session_state.grafico_vazio], theme=choosed_theme)

    c_gtw_condos, c_gtw_pontos = st.columns(2)
    change_center = st.button('Change the map center')
    if change_center:
        mapa_agrupado_por_ponto.update_mapboxes(center=dict(lat=-80, lon=-80))
    c_gtw_condos.plotly_chart(mapa_agrupado_por_ponto, use_container_width=True)
    c_gtw_pontos.plotly_chart(mapa_agrupado_por_sla, use_container_width=True)
    st.plotly_chart(st.session_state.grafico_vazio, use_container_width=True)

    st.markdown('---')
    st.subheader('Comparasion analysis')
    grouped_comparison = pd.DataFrame() # inicializando a variável para não dar erro sem dar o trigger na query
    with st.form('comparison_analysis'):
        c_address_comp, c_resid_comp = st.columns(2)
        addresses_to_compare = c_address_comp.multiselect('Choose any address to compare', options=filtered_data.df['Endereço'].unique())
        condos_to_compare = c_resid_comp.multiselect('Choose any residence to compare', options=filtered_data.df['Grupo - Nome'].unique())
        start_dt_compare = c_address_comp.date_input('Start date', value=datetime.datetime.today() - datetime.timedelta(days=1))
        end_dt_compare = c_resid_comp.date_input('End date', value=datetime.datetime.today())
        submit_comparion = st.form_submit_button('Start comparison')
        if submit_comparion:
            comparison_query = queries_raw_code.individual_comparison(addresses=addresses_to_compare, residences=condos_to_compare, startdt=start_dt_compare, enddt=end_dt_compare)
            comparison_results = pd.DataFrame(tmp_connection.run_single_query(command=comparison_query))
            grouped_comparison = comparison_results.groupby(by=['Grupo - Nome', 'Endereço', 'data snapshot']).agg({'IEF':np.mean}).reset_index()
            grouped_comparison.IEF = grouped_comparison.IEF.round(2)
            grouped_comparison.sort_values(by=['IEF'], ascending=[True], inplace=True)
            st.write(grouped_comparison)

    if grouped_comparison.shape[0] > 0:
        fig_indiv_comparion = individual_comparison.individual_com_figure(data=grouped_comparison)
        st.plotly_chart(fig_indiv_comparion, use_container_width=True)
