# project main code

import streamlit as st
from builders.app_builder import App
from queries import querie_builder, queries_raw_code
import pandas as pd

st.set_page_config(layout='wide', page_title='mapas', initial_sidebar_state='auto')

# app initializer
if __name__ == '__main__':
    app = App(name='laager_dashboards')
    required_data = app.build_app()
    TMP_CONN = querie_builder.Queries(name='cities_queries')
    cities = TMP_CONN.run_single_query(command='SELECT name FROM cities WHERE company_id = 38;')
    main_df = pd.DataFrame(TMP_CONN.run_single_query(command=queries_raw_code.all_units_info(cities=cities['name'])))
    app.apply_styles(style_file='style.css')
    app.start_app(app_session_state=required_data, main_data=main_df)
