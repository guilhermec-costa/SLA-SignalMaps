# project main code

import streamlit as st
from builders.app_builder import App

st.set_page_config(layout='wide', page_title='mapas', initial_sidebar_state='auto')

# app initializer
if __name__ == '__main__':
    app = App(name='laager_dashboards')
    required_data = app.build_app()
    app.apply_styles(style_file='style.css')
    app.start_app(app_session_state=required_data)
