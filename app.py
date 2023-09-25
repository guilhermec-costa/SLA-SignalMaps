# project main code

import streamlit as st
from builders.app_builder import App
import pandas as pd
import session_states

st.set_page_config(layout='wide', page_title='mapas', initial_sidebar_state='auto')

# app initializer
if __name__ == '__main__':
        session_states.initialize_session_states([
                        ('start_querie', False),('ALL_RESULTS', {}), ('clear_cache', False),
                        ('gtw_filters', False), ('extra_selected_condo', []), ('extra_selected_residence', []), ('grouped_points_figure', []),
                        ('grouped_sla_figure', []), ('all_points_figure', []), ('ALL_RESULTS', None), ('polygon_df', pd.DataFrame()), 
                        ('city_filter', []), ('address_filter', []), ('residence_filter', []), ('submit_form_query', False), ('address_comparison', None), ('residence_comparison', None)
                ])
        app = App(name='laager_dashboards')
        required_data = app.build_app()
        app.apply_styles(style_file='style.css')
        app.start_app(app_session_state=required_data)
