import streamlit as st
from queries import queries_raw_code, querie_builder
from figures import individual_comparison, sla_maps, sla_improvement_bar
import datetime
import pandas as pd
import numpy as np
from shapely import Point
from queries import queries_raw_code
from polygons import polygons
from concurrent.futures import ThreadPoolExecutor
from stqdm import stqdm
import session_states
from math import trunc
from queries import data_treatement

INSTALLED_GATEWAYS = [
    'EST SAO JUDAS, 190',
    'R JUAN VICENTE,482',
    'AV PAULO AYRES,75,PARQUE PINHEIROS',
    'R ENG JOAO LANG, 50',
    'R JUBAIR CELESTINO, 195',
    'R PAULA RODRIGUES, 259',
    'R AGOSTINHO NAVARRO, 971',
    'R BACTORIA,174',
    'AV MANOEL PEDRO PIMENTEL, 200',
    'R CATIARA,267,JARDIM UMARIZAL',
    'AV NOVE DE JULHO,544',
    'R MASATO SAKAI,180',
    'AV ODAIR SANTANELLI 100, PARQUE CECAP',
    'AV VIDA NOVA,156',
    'R COM ANTUNES DOS SANTOS, 1640',
    'R TRAJANO REIS, 186',
    'AL CORES DA MATA,1973',
    'R JOSE FERREIRA DE CASTRO,173,VILA AMELIA',
    'AV RAIMUNDO PEREIRA DE MAGALHAES, 12011',
    'AV BUSSOCABA, 850',
    'AL IBERICA,285',
    'AV SARAH VELOSO, 1200',
    'AV ALEXANDRE MACKENZIE, 950',
    'R MARIA DE LURDES GALVAO DE FRANCA, 640',
    'R PAIM,235',
    'R. Bergamota,470',
    'R CAYOWAA,2046',
    'R GAROPA,199',
    'R MANUEL MARTINS COLLACO,246',
    'R CARAPAJO, 124',
    'AV DO CURSINO,6601',
    'AV DNA BLANDINA IGNEZ JULIO, 741',
    'AL CASA BRANCA,343',
    'R PASCOAL RANIERI MAZZILLI,233',
    'R PAULO ROBERTO TRIVELLI, 44',
    'R VICENTE FERREIRA LEITE, 512',
    'TV TRES DE OUTUBRO, 7',
    'R. Camilo, 556',
    'R CANARIO,1111',
    'R JOSE MARIA LISBOA,20',
]
NOT_INSTALLED = [
    'R DR ALFREDO ELLIS,301',
    'R DA CONSOLACAO,3064',
    'AV PE ESTANISLAU DE CAMPOS, 152',
    'AV ENG ALBERTO DE ZAGOTTIS,897',
    'R PROF ARTUR RAMOS,178',
    'AV EDMUNDO AMARAL, 3935'
]

def get_improvement(qtd, ief):
    possible_improvement = (100 - ief)/100
    points_to_improve = trunc(possible_improvement * qtd)
    return points_to_improve

def adjust_blocks(client_name):
    client_name = client_name.__str__()
    if client_name.__contains__(','):
        comma_pos = client_name.find(',')
        return client_name[:comma_pos]
    if client_name.__contains__('-'):
        hifen_pos = client_name.find('-')
        return client_name[:hifen_pos]
    return client_name
    
def geo_comparison(results, profile_to_simulate, connection):

    session_states.initialize_session_states([('polygon_df_first_date', pd.DataFrame()), ('polygon_df_last_date', pd.DataFrame()), ('enable_around_affected_points', False)])
    tmp_connection = querie_builder.Queries(name=connection)
    df_all_unit_services = results['ALL_UNITS']
    jardins_coordenadas = data_treatement.read_data('coordenadas_jardins.csv')
    
    #INSTALLED_GATEWAYS_OF = [gtw for gtw in INSTALLED_GATEWAYS if gtw in df_all_unit_services['Endereço'].unique()]

    st.subheader('Comparasion analysis')
    with st.form('comparison_analysis'):
        if connection == 'laageriotcomgas':
            if profile_to_simulate == 38:
                #default = NOT_INSTALLED
                #default = INSTALLED_GATEWAYS+NOT_INSTALLED
                default = results['ALL_UNITS']['Endereço'][results['ALL_UNITS']['Endereço'].isin(INSTALLED_GATEWAYS+NOT_INSTALLED)].unique()
            else:
                default=[]
        elif connection == 'laageriotsabesp':
            default = []
        c_address_comp, c_resid_comp, c_installations_day = st.columns(3)
        addresses_to_compare = c_address_comp.multiselect('Choose any address to compare', options=df_all_unit_services['Endereço'].unique(), default=default)
        condos_to_compare = c_resid_comp.multiselect('Choose any residence to compare', options=df_all_unit_services['Grupo - Nome'].unique())
        start_dt_compare = c_address_comp.date_input('Start date', value=datetime.datetime.today() - datetime.timedelta(days=1))
        end_dt_compare = c_resid_comp.date_input('End date', value=datetime.datetime.today())
        status_day = c_installations_day.date_input("Installations until: ", value=datetime.datetime.today() - datetime.timedelta(days=1))
        submit_comparion = st.form_submit_button('Start comparison')
        include_around_points = c_address_comp.checkbox('Enable points around')
        if include_around_points:
            st.session_state.enable_around_affected_points = True
        if submit_comparion:
            comparison_query = queries_raw_code.individual_comparison(addresses=addresses_to_compare, residences=condos_to_compare, startdt=start_dt_compare, enddt=end_dt_compare, company_id=profile_to_simulate,
                                                                      connection=connection, installations_until = status_day)
            if comparison_query != "no data":
                
                comparison_results = pd.DataFrame(tmp_connection.run_single_query(command=comparison_query))
                comparison_results['client_name'] = comparison_results['client_name'].apply(lambda x: adjust_blocks(x))
                

                grouped_comparison_per_block = comparison_results.groupby(by=['Grupo - Nome', 'Endereço', 'data snapshot', 'client_name']).agg(qtd=pd.NamedAgg('IEF', aggfunc='count'),
                                                                                                        IEF=pd.NamedAgg('IEF', aggfunc='mean'),
                                                                                                        Latitude=pd.NamedAgg('Latitude', 'mean'),
                                                                                                        Longitude=pd.NamedAgg('Longitude', 'mean')
                                                                                                        ).reset_index()
                
                grouped_comparison_per_qty = comparison_results.groupby(by=['Grupo - Nome', 'Endereço']).agg(qtd=pd.NamedAgg('IEF', aggfunc='count'),
                                                                                        IEF=pd.NamedAgg('IEF', aggfunc='mean'),
                                                                                        ).reset_index()

                grouped_comparison = comparison_results.groupby(by=['Grupo - Nome', 'Endereço', 'data snapshot']).agg(qtd=pd.NamedAgg('IEF', aggfunc='count'),
                                                                                                                      IEF=pd.NamedAgg('IEF', aggfunc='mean'),
                                                                                                                      Latitude=pd.NamedAgg('Latitude', 'mean'),
                                                                                                                      Longitude=pd.NamedAgg('Longitude', 'mean')
                                                                                                                      ).reset_index()
                grouped_comparison.IEF = grouped_comparison.IEF.round(2)
                grouped_comparison.sort_values(by=['IEF'], ascending=[True], inplace=True)
                grouped_comparison_firstday = grouped_comparison[grouped_comparison['data snapshot'] == start_dt_compare]
                grouped_comparison_lastday = grouped_comparison[grouped_comparison['data snapshot'] == end_dt_compare]
                

                if st.session_state.enable_around_affected_points:
                    df_first_date = pd.DataFrame(tmp_connection.run_single_query(command=queries_raw_code.all_units_info(period=start_dt_compare, company_id=profile_to_simulate, connection=connection)))
                    df_last_date = pd.DataFrame(tmp_connection.run_single_query(command=queries_raw_code.all_units_info(period=end_dt_compare, company_id=profile_to_simulate, connection=connection)))

                    df_first_date['Ponto'] = list(zip(df_first_date['Latitude'], df_first_date['Longitude']))
                    df_first_date['Ponto'] = df_first_date['Ponto'].apply(lambda x: Point(x))

                    df_last_date['Ponto'] = list(zip(df_last_date['Latitude'], df_last_date['Longitude']))
                    df_last_date['Ponto'] = df_last_date['Ponto'].apply(lambda x: Point(x))

                    cp_first_day = df_first_date.copy()
                    cp_last_day = df_last_date.copy()
                    lat_list_first_date, lon_list_first_date = grouped_comparison_firstday['Latitude'].to_numpy(), grouped_comparison_firstday['Longitude'].to_numpy()
                    lat_list_last_date, lon_list_last_date = grouped_comparison_lastday['Latitude'].to_numpy(), grouped_comparison_lastday['Longitude'].to_numpy()
                    with ThreadPoolExecutor(4) as executor:
                        list_of_polygons_first_date = list(executor.map(polygons.calculate_polygons, lat_list_first_date, lon_list_first_date, [1000]*len(lat_list_first_date)))
                        list_of_polygons_last_date = list(executor.map(polygons.calculate_polygons, lat_list_last_date, lon_list_last_date, [1000]*len(lat_list_last_date)))
                        
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
                sla_map_left = sla_maps.plot_sla_map(data_sla=affected_points_first_date, title=f'Snapshot {start_dt_compare}', colmn_to_base_color='IEF', group_type='IEF', theme='carto-darkmatter', include_bu_city_info=False)
                sla_map_right = sla_maps.plot_sla_map(data_sla=affected_points_last_date, title=f'Snapshot {end_dt_compare}', colmn_to_base_color='IEF', group_type='IEF', theme='carto-darkmatter', include_bu_city_info=False)
                start_date_sla = affected_points_first_date.IEF.mean()
                end_date_sla = affected_points_last_date.IEF.mean()
                start_date_shape = affected_points_first_date.shape[0]
                end_date_shape = affected_points_last_date.shape[0]
                st.session_state.enable_around_affected_points = False

            else:
                start_date_sla = grouped_comparison_firstday.IEF.mean()
                end_date_sla = grouped_comparison_lastday.IEF.mean()
                
                not_communcating = round((100 - end_date_sla)/100 * grouped_comparison_lastday.qtd, 0)
                start_date_shape = grouped_comparison_firstday.shape[0]
                end_date_shape = grouped_comparison_lastday.shape[0]
                sla_map_left = sla_maps.plot_sla_map(data_sla=grouped_comparison_firstday, title=f'Snapshot {start_dt_compare}', colmn_to_base_color='IEF', group_type='IEF', theme='carto-darkmatter', include_bu_city_info=False)
                sla_map_right = sla_maps.plot_sla_map(data_sla=grouped_comparison_lastday, title=f'Snapshot {end_dt_compare}', colmn_to_base_color='IEF', group_type='IEF', theme='carto-darkmatter', include_bu_city_info=False)
            sla_maps.add_traces_on_map(sla_map_left, another_data=jardins_coordenadas, name='Jardins Area', fillcolor='rgba(31, 54, 251, 0.3)')
            sla_maps.add_traces_on_map(sla_map_right, another_data=jardins_coordenadas, name='Jardins Area', fillcolor='rgba(31, 54, 251, 0.3)')
            st.markdown('---')
            map_left.metric(f'SLA on {start_dt_compare}', value=f'{round(start_date_sla, 2)}%', delta=start_date_shape)
            map_left.metric(f'Affected points on {start_dt_compare}', value=start_date_shape, delta=0)
            # map_left.write(f'Existing points on map: {start_date_shape}')
            
            diff = round(end_date_sla - start_date_sla)
            possible_improvement = round((100 - end_date_sla), 2)
            possible_points_to_solve = trunc((possible_improvement/100) * grouped_comparison_lastday.qtd.sum())
            map_right.metric(f'SLA on {end_dt_compare}', value=f'{round(end_date_sla, 2)}%', delta=end_date_shape)
            map_right.metric(f'Affected points on {end_dt_compare}', value=end_date_shape, delta=end_date_shape - start_date_shape)
            st.metric(f'Possible SLA improvement: ', value=possible_improvement,
                             help=f'{possible_points_to_solve} installations')
            # map_right.write(f'Existing points on map: {end_date_shape}')
            map_left.plotly_chart(sla_map_left, use_container_width=True)
            map_right.plotly_chart(sla_map_right, use_container_width=True)
            
            grouped_comparison_lastday['points_to_improve'] = grouped_comparison_lastday[['qtd', 'IEF']].apply(lambda row: get_improvement(row.qtd, row.IEF), axis=1)
            
            st.subheader('Análise de repetidores')
            per_block, per_qty = st.columns(2)
            #st.write(comparison_results.sort_values(by=['Grupo - Nome', 'client_name'], ascending=[True, True]))
            grouped_comparison_per_block["improve"] = np.ceil((100 - grouped_comparison_per_block["IEF"])/100 * grouped_comparison_per_block["qtd"])
            grouped_comparison_per_block.sort_values(by=['Grupo - Nome', 'improve'], inplace=True, ascending=[True, False])
            per_block.write(grouped_comparison_per_block[grouped_comparison_per_block["data snapshot"] == end_dt_compare ])
            
            grouped_comparison_lastday.sort_values(by=['points_to_improve'], ascending=False, inplace=True)
            per_qty.write(grouped_comparison_lastday)
            #st.write(grouped_comparison_lastday)
            improvement_sla_fig = sla_improvement_bar.sla_improvement(grouped_comparison_lastday, xaxes='Endereço', yaxes='points_to_improve')
            st.plotly_chart(improvement_sla_fig, use_container_width=True)
        with tab_bars:
            st.write(grouped_comparison.sort_values(by='qtd', ascending=False))
            fig_indiv_comparion = individual_comparison.individual_com_figure(data=grouped_comparison.sort_values(by="qtd"), start_date=start_dt_compare, end_date=end_dt_compare)
            st.plotly_chart(fig_indiv_comparion, use_container_width=True)

    except:
        pass
