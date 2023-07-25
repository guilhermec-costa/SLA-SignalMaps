# project main code
import streamlit as st
from queries import querie_builder
from queries.all_queries import queries_constants
from streamlit_option_menu import option_menu
from typing import Dict
import importlib
import session_states
from PIL import Image
# from rembg import remove

st.set_page_config(layout='wide', page_title='mapas', initial_sidebar_state='auto')

def main_sidebar() -> Dict:
    laager_logo = Image.open('logos/logo_laager.jpg')
    # output_image = 'logos/logo_laager_nobg.jpg'
    # output = remove(laager_logo)
    # output.save(output_image)
    map_app_tabs = {'SLA overview metrics': 'sla_overview', 'Geographic SLA analysis': 'geospacial_analysis'}
    with st.sidebar:
        st.image(laager_logo)
        selected_menu = option_menu('Dashboards Laager', options=[
            'SLA overview metrics', 'Geographic SLA analysis'
        ], default_index=0, orientation='vertical', menu_icon='menu-button-wide',
            styles={
        "container": {"padding": "0!important", "background-color": "#0E1117", "border-radius":"6px", "height":"300px", "font-weight":"bold"},
        "icon": {"color": "#13CF29", "font-size": "25px"}, 
        "nav-link": {"font-size": "23px", "text-align": "left", "margin":"0px", "--hover-color": "##7FA6EB", "font-family":"roboto", "padding-top":"20px"},
        "nav-link-selected": {"background-color": "#7CC7FF"},
    })
    return 'views.' + map_app_tabs.get(selected_menu)


if __name__ == '__main__':
    with open('style.css') as style:
        st.markdown(f'<style>{style.read()}</style>', unsafe_allow_html=True)

    session_states.initialize_session_states([('start_querie', False), ('ALL_RESULTS', None), ('clear_cache', False)])
    queries_instancy = querie_builder.Queries(name='laager_queries')
    connection_state = queries_instancy.verify_connection()
    if connection_state == 'success':
        st.success('Connection succeded!')
        queries_instancy.add_queries(queries_constants)
        c_start_querie, c_clear_cache, *_ = st.columns(9, gap='small')
        start_querie = c_start_querie.button('Start queries', key='start_queries', type='primary')
        clear_cache = c_clear_cache.button('Clear data caches and resource caches', key='clearcache', type='primary')
        if clear_cache:
            st.cache_data.clear()

            st.session_state.clear_cache = False

        if start_querie:
            st.session_state.start_querie = False
            with st.spinner('Running queries...'):
                queries_instancy.run_queries(queries_instancy.all_queries_commands)
                st.session_state.ALL_RESULTS = queries_instancy.get_query_result()
        if st.session_state.ALL_RESULTS is not None:
            choosed_app = main_sidebar()
            choosed_module = importlib.import_module(choosed_app)
            if choosed_module.__name__ == 'views.sla_overview':
                choosed_module.sla_overview(results=st.session_state.ALL_RESULTS)
            elif choosed_module.__name__ == 'views.geospacial_analysis':
                choosed_module.geo_analysis(results=st.session_state.ALL_RESULTS)
    