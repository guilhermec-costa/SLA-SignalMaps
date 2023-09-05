import streamlit as st
from queries import queries_raw_code, querie_builder
from figures import individual_comparison, sla_maps
import datetime
import pandas as pd
import numpy as np
from shapely import Point
from queries import queries_raw_code
from polygons import polygons
from concurrent.futures import ThreadPoolExecutor
from stqdm import stqdm
import session_states

def geo_comparison(results, profile_to_simulate):

    session_states.initialize_session_states([('polygon_df_first_date', pd.DataFrame()), ('polygon_df_last_date', pd.DataFrame()), ('enable_around_affected_points', False)])
    tmp_connection = querie_builder.Queries(name='temporary_queries_comparison')
    df_all_unit_services = results['ALL_UNITS']

    st.subheader('Comparasion analysis')
    with st.form('comparison_analysis'):
        c_address_comp, c_resid_comp = st.columns(2)
        addresses_to_compare = c_address_comp.multiselect('Choose any address to compare', options=df_all_unit_services['Endereço'].unique())
        condos_to_compare = c_resid_comp.multiselect('Choose any residence to compare', options=df_all_unit_services['Grupo - Nome'].unique())
        start_dt_compare = c_address_comp.date_input('Start date', value=datetime.datetime.today() - datetime.timedelta(days=1))
        end_dt_compare = c_resid_comp.date_input('End date', value=datetime.datetime.today())
        submit_comparion = st.form_submit_button('Start comparison')
        include_around_points = c_address_comp.checkbox('Enable points around')
        if include_around_points:
            st.session_state.enable_around_affected_points = True
        if submit_comparion:
            df_first_date = pd.DataFrame(tmp_connection.run_single_query(command=queries_raw_code.all_units_info(period=start_dt_compare, company_id=profile_to_simulate)))
            df_last_date = pd.DataFrame(tmp_connection.run_single_query(command=queries_raw_code.all_units_info(period=end_dt_compare, company_id=profile_to_simulate)))

            df_first_date['Ponto'] = list(zip(df_first_date['Latitude'], df_first_date['Longitude']))
            df_first_date['Ponto'] = df_first_date['Ponto'].apply(lambda x: Point(x))

            df_last_date['Ponto'] = list(zip(df_last_date['Latitude'], df_last_date['Longitude']))
            df_last_date['Ponto'] = df_last_date['Ponto'].apply(lambda x: Point(x))

            cp_first_day = df_first_date.copy()
            cp_last_day = df_last_date.copy()



            comparison_query = queries_raw_code.individual_comparison(addresses=addresses_to_compare, residences=condos_to_compare, startdt=start_dt_compare, enddt=end_dt_compare, company_id=profile_to_simulate)
            if comparison_query != "no data":

                comparison_results = pd.DataFrame(tmp_connection.run_single_query(command=comparison_query))
                grouped_comparison = comparison_results.groupby(by=['Grupo - Nome', 'Endereço', 'data snapshot']).agg({'IEF':np.mean, 'Latitude':np.mean, 'Longitude':np.mean}).reset_index()
                grouped_comparison.IEF = grouped_comparison.IEF.round(2)
                grouped_comparison.sort_values(by=['IEF'], ascending=[True], inplace=True)
                grouped_comparison_firstday = grouped_comparison[grouped_comparison['data snapshot'] == start_dt_compare]
                grouped_comparison_lastday = grouped_comparison[grouped_comparison['data snapshot'] == end_dt_compare]


                if st.session_state.enable_around_affected_points:
                    with st.spinner('Calculate polygons...'):
                        lat_list_first_date, lon_list_first_date = grouped_comparison_firstday['Latitude'].to_numpy(), grouped_comparison_firstday['Longitude'].to_numpy()
                        lat_list_last_date, lon_list_last_date = grouped_comparison_lastday['Latitude'].to_numpy(), grouped_comparison_lastday['Longitude'].to_numpy()
                        with ThreadPoolExecutor(4) as executor:
                            list_of_polygons_first_date = list(executor.map(polygons.calculate_polygons, lat_list_first_date, lon_list_first_date, [5000]*len(lat_list_first_date)))
                            list_of_polygons_last_date = list(executor.map(polygons.calculate_polygons, lat_list_last_date, lon_list_last_date, [5000]*len(lat_list_last_date)))
                        
                        contained_index_first_date = []
                        contained_index_last_date = []
                        with st.spinner('Calculating polygons...'):
                            with ThreadPoolExecutor(4) as executor:
                                for n in stqdm(range(len(lat_list_first_date))):
                                    current_polygon_first_date, current_list_of_circles_first_date = list_of_polygons_first_date[n][0], list_of_polygons_first_date[n][1]
                                    current_polygon_last_date, current_list_of_circles_last_date = list_of_polygons_last_date[n][0], list_of_polygons_last_date[n][1]
                                    args_first_date = [(index, row[-1], current_polygon_first_date) for index, *row in df_first_date.itertuples()]
                                    args_last_date = [(index, row[-1], current_polygon_last_date) for index, *row in df_last_date.itertuples()]
                                    results_first_date = executor.map(polygons.check_if_pol_contains, args_first_date)
                                    results_last_date = executor.map(polygons.check_if_pol_contains, args_last_date)
                                    contained_index_first_date.extend([i for i in results_first_date if i is not None])
                                    contained_index_last_date.extend([i for i in results_last_date if i is not None])

                                    df_first_date = df_first_date[~df_first_date.index.isin(contained_index_first_date)]
                                    df_last_date = df_last_date[~df_last_date.index.isin(contained_index_last_date)]
               


                    affected_points_first_date = cp_first_day.loc[contained_index_first_date]
                    affected_points_first_date.drop_duplicates(subset=['Matrícula'], inplace=True)
                    affected_points_last_date = cp_last_day.loc[contained_index_last_date]
                    affected_points_first_date.drop_duplicates(subset=['Matrícula'], inplace=True)
                    with st.expander('See filtered data'):
                        tab_first_day, tab_last_day = st.columns(2)
                        tab_first_day.subheader(f'Affected points on snapshot from {start_dt_compare}')
                        tab_first_day.write(affected_points_first_date)
                        tab_last_day.subheader(f'Affected points on snapshot from {end_dt_compare}')
                        tab_last_day.write(affected_points_last_date)

        
    tab_maps, tab_bars = st.tabs(['SLA Maps', 'Indivual Comparisons'])
    try:
        with tab_maps:
            map_left, map_right = st.columns(2)
            
            if st.session_state.enable_around_affected_points:
                st.session_state.enable_around_affected_points = False
                sla_map_left = sla_maps.plot_sla_map(data_sla=affected_points_first_date, title=f'Snapshot {start_dt_compare}', colmn_to_base_color='IEF', group_type='IEF', theme='carto-darkmatter', include_bu_city_info=False)
                sla_map_right = sla_maps.plot_sla_map(data_sla=affected_points_last_date, title=f'Snapshot {end_dt_compare}', colmn_to_base_color='IEF', group_type='IEF', theme='carto-darkmatter', include_bu_city_info=False)
                map_left.write(affected_points_first_date.IEF.mean())
                map_left.write(affected_points_first_date.shape[0])
                map_right.write(affected_points_last_date.IEF.mean())
                map_right.write(affected_points_last_date.shape[0])

            else:
                sla_map_left = sla_maps.plot_sla_map(data_sla=grouped_comparison_firstday, title=f'Snapshot {start_dt_compare}', colmn_to_base_color='IEF', group_type='IEF', theme='carto-darkmatter', include_bu_city_info=False)
                sla_map_right = sla_maps.plot_sla_map(data_sla=grouped_comparison_lastday, title=f'Snapshot {end_dt_compare}', colmn_to_base_color='IEF', group_type='IEF', theme='carto-darkmatter', include_bu_city_info=False)

            map_left.plotly_chart(sla_map_left, use_container_width=True)
            map_right.plotly_chart(sla_map_right, use_container_width=True)
        with tab_bars:
            fig_indiv_comparion = individual_comparison.individual_com_figure(data=grouped_comparison, start_date=start_dt_compare, end_date=end_dt_compare)
            st.plotly_chart(fig_indiv_comparion, use_container_width=True)

    except:
        pass
