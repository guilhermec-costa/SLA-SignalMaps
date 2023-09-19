import streamlit as st
from typing import Union, Dict
from queries import querie_builder
from views import main_sidebar
import importlib
from queries import queries_raw_code

class App:
    company_map = {
        'Comgás':38,
        'Sanasa':34,
        'Sabesp':4,
    }

    def __init__(self, name) -> None:
        self.app_name = name
        self.choosed_connection = None

    def apply_styles(self, style_file:str) -> None:
        with open(style_file) as style:
            st.markdown(f'<style>{style.read()}</style>', unsafe_allow_html=True)

    def start_app(self, app_session_state) -> None:
        if app_session_state != 'Error on connect to the database' and st.session_state.ALL_RESULTS != {}:
                
            #choosed_app, profile_to_simulate = main_sidebar.main_sidebar()
            choosed_module = importlib.import_module(self.choosed_app)
            module_name = choosed_module.__name__
            function_name = main_sidebar.module_mapping[module_name]
            choosed_function = getattr(choosed_module, function_name)
            choosed_function(results=st.session_state.ALL_RESULTS, profile_to_simulate=self.profile_to_simulate,
                             connection=self.choosed_connection)
    
    def build_app(self) -> Union[Dict, str]:
        st.cache_resource.clear()
        # st.cache_data.clear()
        self.choosed_connection = 'laageriotcomgas'
        queries_instancy = querie_builder.Queries(name=self.choosed_connection)
        connection_state = queries_instancy.verify_connection()
        if connection_state == 'success':
            self.choosed_app, profile_to_simulate = main_sidebar.main_sidebar()
            self.profile_to_simulate = self.company_map[profile_to_simulate]
            st.write('perfil de simulação: ', self.profile_to_simulate)
            st.success('Connection succeded!')
            c_start_querie, c_clear_cache, _, stop_queries, *_ = st.columns(10, gap='small')
            start_querie = c_start_querie.button('Sync database', key='start_queries', type='primary')
            clear_cache = c_clear_cache.button('Clear caches', key='clearcache', type='primary')
            if clear_cache:
                st.cache_data.clear()
                st.session_state.clear_cache = False

            if start_querie:
                st.write(queries_instancy.connection)
                st.session_state.start_querie = False
                stop_querie_flag = stop_queries.button('Stop queries', type='secondary')
                if not stop_querie_flag:
                    with st.spinner('Running queries.'):
                        
                        # extração de todos os dados necessários para todar a aplicação
                        main_df = queries_instancy.run_single_query(command=queries_raw_code.all_units_info(company_id=self.profile_to_simulate,
                                                                                                            connection= self.choosed_connection))
                        #recente_readings = queries_instancy.run_single_query(command=queries_raw_code.recent_readings(company_id=self.profile_to_simulate))
                        port_zero = queries_instancy.run_single_query(command=queries_raw_code.port_zero(company_id=self.profile_to_simulate,
                                                                                                         connection= self.choosed_connection))
                        sla_over_time = queries_instancy.run_single_query(command=queries_raw_code.sla_over_time_all_units(company_id=self.profile_to_simulate,
                                                                                                                           connection= self.choosed_connection))

                        #st.session_state.ALL_RESULTS = queries_instancy.run_queries(queries_instancy.all_queries_commands)
                        st.session_state.ALL_RESULTS['ALL_UNITS'] = main_df
                        st.session_state.ALL_RESULTS['SLA_OVER_TIME_ALL_UNITS'] = sla_over_time
                        #st.session_state.ALL_RESULTS['RECENT_READINGS'] = recente_readings
                        st.session_state.ALL_RESULTS['PORT_ZERO'] = port_zero
                    stop_querie_flag = st.empty()

            return st.session_state.ALL_RESULTS, self.profile_to_simulate
        return 'Error on connect to the database'
