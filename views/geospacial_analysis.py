# geospacial analysis code
import streamlit as st
import datetime
from queries import querie_builder, data_treatement
from shapely import Point
from filters import Filters
from figures import sla_maps, stastics_fig, update_figs_layout
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from stqdm import stqdm
from polygons import polygons
import pandas as pd
from queries import queries_raw_code
import session_states
import googlemaps
import json
from .comparisons import get_improvement, INSTALLED_GATEWAYS, NOT_INSTALLED
from math import trunc
import time

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def geo_analysis(results: querie_builder.Queries, profile_to_simulate, connection):
    # inicialização das variáveis de sessão
    session_states.initialize_session_states([('main_data', pd.DataFrame()), ('grouped_data', pd.DataFrame()), ('general_data', pd.DataFrame())])

    #inicilização da API do Google
    gmaps = googlemaps.Client(key=st.secrets.googleapi.apikey)

    # variável de conexão temporária
    tmp_connection = querie_builder.Queries(name=connection)

    #inicialização dos dados necessários
    jardins_coordenadas = data_treatement.read_data('coordenadas_jardins.csv')
    df_all_unit_services = results['ALL_UNITS']
    df_all_unit_services['Ponto'] = list(zip(df_all_unit_services['Latitude'], df_all_unit_services['Longitude']))
    df_all_unit_services['Ponto'] = df_all_unit_services['Ponto'].apply(lambda x: Point(x))

    agrupado_por_condo = df_all_unit_services.groupby(by=['Unidade de Negócio - Nome','Cidade - Nome', 'Grupo - Nome', 'Endereço']).agg({'IEF':np.mean, 'Matrícula':'count', 'Latitude':np.mean, 'Longitude':np.mean}).reset_index()
    agrupado_por_condo.IEF = agrupado_por_condo.IEF.apply(lambda x: round(x, 2))
    
    st.markdown('---')
    st.subheader('Filters')
    filtered_group = Filters(agrupado_por_condo)
    filtered_data = Filters(df_all_unit_services)
    
    # Formulários pra filtros de queries
    with st.form(key='submit_sla_form'):
        c_BU, c_city = st.columns(2)
        filtro_BU = c_BU.multiselect('Business Unit', options=filtered_data.df['Unidade de Negócio - Nome'].unique(), key='bu_filter')
        st.session_state.city_filter = c_city.multiselect('City', options=filtered_data.df['Cidade - Nome'].unique(), key='cityfilter')
        
        c_address, c_group = st.columns(2)
        st.session_state.address_filter = c_address.multiselect('Address name', options=filtered_data.df['Endereço'].unique())
        st.session_state.residence_filter = c_group.multiselect('Residence name', options=filtered_data.df['Grupo - Nome'].unique())

        c_num_min, c_num_max, c_status_date = st.columns(3)


        min_pontos = c_num_min.number_input('Min number of installations:', min_value=0, value=0)
        max_pontos = c_num_max.number_input('Max number of installations:', min_value=0, value=5000)

        status_date = c_status_date.date_input('Day of the status', value=datetime.datetime.today(), max_value=datetime.datetime.today())
        min_sla_condo, max_sla_condo = c_num_min.slider('SLA por condomínio', min_value=0.0, max_value=100.0, value=[float(filtered_group.df.IEF.min()),float(filtered_group.df.IEF.max())], step=5.0)
        min_sla_pontos, max_sla_pontos = c_num_max.slider('SLA por instalação', min_value=0.0, max_value=100.0, value=[float(filtered_data.df.IEF.min()),float(filtered_data.df.IEF.max())], step=5.0, key='sla_slider_pontos')
        submit_form = st.form_submit_button('Submit the form')
        if submit_form:
            # caso o botão seja apertado, uma query individual é disparada com os filtros
            new_query = queries_raw_code.all_units_info(status_date, bussiness_unts=filtro_BU, cities=st.session_state.city_filter, addresses=st.session_state.address_filter, residences=st.session_state.residence_filter,
                                                        company_id=profile_to_simulate, connection=connection)

            filtered_data.df  = pd.DataFrame(tmp_connection.run_single_query(command=new_query))
            filtered_data.general_qty_filter(min_sla_pontos, max_sla_pontos, 'IEF')

            filtered_data.validate_filter('general_filter', st.session_state.city_filter, refer_column='Cidade - Nome')

            filtered_group.df = filtered_data.df.groupby(by=['Unidade de Negócio - Nome','Cidade - Nome', 'Grupo - Nome', 'Endereço'])\
            .agg({'IEF':np.mean, 'Matrícula':'count', 'Latitude':np.mean, 'Longitude':np.mean, 'data snapshot':np.max}).reset_index()
            
            filtered_group.df.IEF = filtered_group.df.IEF.apply(lambda x: round(x, 2))
            results['ALL_UNITS'] = filtered_data.df

    filtered_group.df = filtered_group.df[(filtered_group.df['Matrícula'] >= min_pontos) &
                                (filtered_group.df['Matrícula'] <= max_pontos) &
                                (filtered_group.df['IEF'] >= min_sla_condo) & (filtered_group.df['IEF'] <= max_sla_condo)]

    
    # faz com que, quando o dataframe agrupado por endereço mude, o dataframe com todos os pontos mude também
    filtered_data.df = filtered_data.df[filtered_data.df['Endereço'].isin(filtered_group.df['Endereço'])]
    filtered_data.df.sort_values(by='IEF', ascending=False, inplace=True)
    cp_main_data = filtered_data.df.copy()
    
    filtered_group.df.rename(columns={'Matrícula':'Pontos instalados'}, inplace=True)
    # expander para exibição de dados filtrados
    with st.expander('Filtered data:'):
        filtered_group.df["improve"] = np.ceil((100 - filtered_group.df["IEF"])/100 * filtered_group.df["Pontos instalados"])
        filtered_group.df.sort_values(by='improve', ascending=False, inplace=True)
        st.write(filtered_group.df)
        st.markdown('---')
        st.write(filtered_data.df)
        
        dados = convert_df(filtered_data.df)
        date = filtered_data.df['data snapshot'].unique()[0]
        st.download_button(
            label='Download data', data=dados,
            file_name=f'SLA_data_{date}.csv', mime='text/csv')

    # resumo de métricas dos dados filtrados
    theme_position, ponto_filtrado, sla_filtrado, opc_agrupamento, *_ = st.columns(5)
    theme_position.metric('Addresses:', f'{filtered_group.df.shape[0]}')
    ponto_filtrado.metric('Installations:', f'{filtered_group.df["Pontos instalados"].sum()}')
    sla_filtrado.metric('Filtered SLA %', value=f'{round(np.mean(filtered_group.df.IEF), 2)}%')
    st.markdown('---')
    
    st.session_state.all_points_figure = sla_maps.plot_sla_map(filtered_data.df, title='SLA % per installation', colmn_to_base_color='IEF', theme='streets', group_type='IEF')
    st.session_state.grouped_points_figure = sla_maps.plot_sla_map(filtered_group.df, title=f'Installations per address', theme='streets', group_type='Pontos instalados',
                                        colmn_to_base_color='Unidade de Negócio - Nome')
    st.session_state.grouped_sla_figure = sla_maps.plot_sla_map(filtered_group.df, title=f'SLA % mean grouped per address', theme='streets', group_type='IEF',
                                        colmn_to_base_color='IEF')

    sla_maps.add_traces_on_map(st.session_state.all_points_figure, another_data=jardins_coordenadas, name='Jardins Area', fillcolor='rgba(31, 54, 251, 0.3)')
    sla_maps.add_traces_on_map(st.session_state.grouped_points_figure, another_data=jardins_coordenadas, name='Jardins Area', fillcolor='rgba(31, 54, 251, 0.3)')
    sla_maps.add_traces_on_map(st.session_state.grouped_sla_figure, another_data=jardins_coordenadas, name='Jardins Area', fillcolor='rgba(32, 54, 251, 0.3)')
    
    
    try:
        with st.expander(label='SLA Descriptive analysis'):
            metricas_sla_indiv = filtered_data.df.describe().drop('count', axis=0).reset_index().rename(columns={'index':'metricas'})
            metricas_sla_indiv.IEF = metricas_sla_indiv.IEF.apply(lambda x: round(x, 2))
            metricas_sla_indiv.metricas = ['SLA % mean', 'Standard deviation', 'Minimum SLA %', '25% of the data', '50% of the data', '75% of the data', 'Maximum SLA %']
            fig_descritiva = stastics_fig.analise_descritiva(metricas_sla_indiv)
            st.plotly_chart(fig_descritiva, use_container_width=True)
        st.markdown('---')
    except:
        pass


    qty_that_is_contained = 0
    # formulário de configuração para cálculo de alcance de gateways
    st.subheader('Gateways analysis')
    with st.expander('Edit gateway options'):
        with st.form('gtw_form', clear_on_submit=False):
            c_gtw_number, c_gtw_range = st.columns(2)
            #qty_of_gtw = c_gtw_number.number_input('Distribute some gateways: ', min_value=0, max_value=filtered_group.df['Pontos instalados'].max())
            if connection == 'laageriotcomgas':
                if profile_to_simulate == 38:
                    #default = NOT_INSTALLED
                    #default = INSTALLED_GATEWAYS+NOT_INSTALLED
                    default = results['ALL_UNITS']['Endereço'][results['ALL_UNITS']['Endereço'].isin(INSTALLED_GATEWAYS+NOT_INSTALLED)].unique()
                else:
                    default=[]
            elif connection == 'laageriotsabesp':
                default = []

            st.session_state.extra_selected_address = c_gtw_number.multiselect('Or choose any address', options=results['ALL_UNITS']['Endereço'].unique(), key='address',
                                                                               default=default)
            st.session_state.extra_selected_residence = c_gtw_range.multiselect('Or choose any residence name', options=results['ALL_UNITS']['Grupo - Nome'].unique(), key='residence')

            personalized_gtw = results['ALL_UNITS'][(results['ALL_UNITS']['Endereço'].isin(st.session_state.extra_selected_address)) | 
                                                             (results['ALL_UNITS']['Grupo - Nome'].isin(st.session_state.extra_selected_residence))]
        
            gtw_range = c_gtw_range.number_input('Gateway range in meters: ', min_value=1, value=1000)

            grouped_personalized = personalized_gtw.groupby(by=['Unidade de Negócio - Nome','Cidade - Nome', 'Grupo - Nome', 'Endereço']).agg({'IEF':np.mean, 'Matrícula':'count', 'Latitude':np.mean, 'Longitude':np.mean}).reset_index()
            #df_filtered_per_points = filtered_group.df.sort_values(by='Pontos instalados', ascending=False).iloc[:int(qty_of_gtw), :].reset_index()
            #df_filtered_per_points = pd.concat([df_filtered_per_points, personalized_gtw.reset_index()], ignore_index=True)
            grouped_personalized.sort_values(by='Matrícula', ascending=False, ignore_index=True, inplace=True)
            grouped_personalized.drop_duplicates(subset=['Endereço'], inplace=True, ignore_index=True, keep='first')
            if profile_to_simulate == 38: # ou seja, é comgas, então drope condomínio duplicados
                grouped_personalized.drop_duplicates(subset=['Grupo - Nome'], inplace=True, ignore_index=True, keep='first')
            submit_gtw = st.form_submit_button('Start calculations')
            st.subheader('Ordem de prioridade para instalação de gateways')
            st.write(grouped_personalized)
            if submit_gtw: st.session_state.gtw_filters = True
                
    if st.session_state.gtw_filters:
        st.session_state.gtw_filters = False
        
        # lista de latitudes e longitudes centrais para cada endereço
        lat_list, lon_list = grouped_personalized['Latitude'].to_numpy(), grouped_personalized['Longitude'].to_numpy()
        with ThreadPoolExecutor(4) as executor:
            list_of_polygons = list(executor.map(polygons.calculate_polygons, lat_list, lon_list, [gtw_range]*len(lat_list)))
        
        contained_index = []
        with st.spinner('Calculating polygons...'):
            # concorrência para cálculo de pontos afetados e plottagem dos polígonos nos gráficos
            array_of_points = np.array(cp_main_data["Ponto"])
            #start = time.perf_counter()
            INSTALLED_COLOR = 'rgba(55, 189, 115, 0.6)'
            NOT_INSTALLED_COLOR = 'rgba(249, 63, 30, 0.8)'
            with ThreadPoolExecutor(4) as executor:
                for n in stqdm(range(len(lat_list))):
                    current_polygon, current_list_of_circles = list_of_polygons[n][0], list_of_polygons[n][1]
                    
                    temporary_lats = [tuple_of_coords[0] for tuple_of_coords in current_list_of_circles]
                    temporary_longs = [tuple_of_coords[1] for tuple_of_coords in current_list_of_circles]
                    st.session_state.polygon_df = pd.DataFrame(data={'Latitude':temporary_lats, 'Longitude':temporary_longs})


                    #args = [(index, row, current_polygon) for index, row in enumerate(array_of_points)]
                    args = [(index, row[-1], current_polygon) for index, *row in cp_main_data.itertuples()]
                    results = executor.map(polygons.check_if_pol_contains, args)
                    contained_index.extend([i for i in results if i is not None])
                    
                    cp_main_data = cp_main_data[~cp_main_data.index.isin(contained_index)]
                    
                     
                    color = INSTALLED_COLOR if grouped_personalized.loc[n:n, 'Endereço'].values[0] in INSTALLED_GATEWAYS else NOT_INSTALLED_COLOR

                    if st.session_state.polygon_df is not None:
                        sla_maps.add_traces_on_map(st.session_state.grouped_points_figure, another_data=st.session_state.polygon_df, fillcolor=color, name=grouped_personalized.loc[n:n, 'Endereço'].values[0])
                        sla_maps.add_traces_on_map(st.session_state.grouped_sla_figure, another_data=st.session_state.polygon_df, fillcolor=color, name=grouped_personalized.loc[n:n, 'Endereço'].values[0])                 
                        sla_maps.add_traces_on_map(st.session_state.all_points_figure, another_data=st.session_state.polygon_df, fillcolor=color, name=grouped_personalized.loc[n:n, 'Endereço'].values[0])
        
        #end = time.perf_counter()
        #print('Tempo demorado: ', end - start)
        affected_points = filtered_data.df.loc[contained_index]
        affected_points.drop_duplicates(subset=['Matrícula'], inplace=True)
        qty_that_is_contained = affected_points.shape[0]
        points_metrics, choosed_gtw_qtd, sla_metrics, sla_prevision, communicating = st.columns(5)
        
        if grouped_personalized.shape[0] >= 1:
            mean_sla_affecteds = round(affected_points['IEF'].mean(), 2)
            points_metrics.metric(f'Affected points', value=f'{qty_that_is_contained} pontos')
            choosed_gtw_qtd.metric('Quantity of gateways: ', value=f'{len(lat_list)} gateways')
            sla_metrics.metric(f'Filtered SLA %', value=mean_sla_affecteds)

            improvement_preview = round(trunc(qty_that_is_contained - ((mean_sla_affecteds/100) * qty_that_is_contained)) / filtered_data.df.shape[0] * 100, 2)
            sla_prevision.metric('Improvement preview over the general SLA %', value=f'{improvement_preview}%', help=f"Considering {filtered_data.df.shape[0]} points")

            with st.expander('Addresses and installations affected'):
                st.write(affected_points)
                st.write(filtered_group.df[filtered_group.df['Endereço'].isin(affected_points['Endereço'].unique())].sort_values(by='Pontos instalados', ascending=False))
    
    with st.form(key='change_location'):
        go_to_location = st.text_input('Type a location to go')
        confirm_location = st.form_submit_button('Change location')
        if confirm_location:
            geocode_result = gmaps.geocode(go_to_location)
            converted_to_json = json.dumps(geocode_result)
            location = geocode_result[0]['geometry']['location']
            lat, lon = location['lat'], location['lng']
            st.session_state.all_points_figure.update_mapboxes(center=dict(lat=lat, lon=lon), zoom=16)
            st.session_state.grouped_sla_figure.update_mapboxes(center=dict(lat=lat, lon=lon), zoom=16)
            st.session_state.grouped_points_figure.update_mapboxes(center=dict(lat=lat, lon=lon), zoom=16)
    
    theme_position, *_ = st.columns(5)
    theme_options = ['carto-darkmatter', 'satellite-streets', 'open-street-map', 'satellite', 'streets', 'carto-positron', 'dark', 'stamen-terrain', 'stamen-toner',
                        'stamen-watercolor', 'basic', 'outdoors', 'light', 'white-bg']
    choosed_theme = theme_position.selectbox('Choose any theme', options=theme_options, index=0)
    update_figs_layout.update_fig_layouts([st.session_state.grouped_points_figure, st.session_state.grouped_sla_figure, st.session_state.all_points_figure], theme=choosed_theme)
    
    # def handle_selection(event, eventdata):
    #     st.write('NA FUNÇÃO')
    #     if eventdata:
    #         selected_points = eventdata["Latitude"]
    #         st.write(selected_points)
            
    tab_grouped_condo, tab_grouped_sla, tab_all_points = st.tabs(['SLA map grouped by address', 'SLA map grouped by average SLA', 'SLA map - All points'])
    with tab_grouped_condo:
        st.plotly_chart(st.session_state.grouped_points_figure, use_container_width=True)
        #st.session_state.grouped_points_figure.data[0].on_selection(handle_selection)
    with tab_grouped_sla:
        st.plotly_chart(st.session_state.grouped_sla_figure, use_container_width=True)
    with tab_all_points:
        st.plotly_chart(st.session_state.all_points_figure, use_container_width=True)


