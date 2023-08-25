from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu

module_mapping = {'views.sla_overview':'sla_overview',
                  'views.geospacial_analysis':'geo_analysis',
                  'views.comparisons':'geo_comparison'
                }

def main_sidebar() -> str:
    laager_logo = Image.open('logos/laager_logo.png')
    map_app_tabs = {'SLA overview metrics': 'sla_overview', 'Geographic SLA analysis': 'geospacial_analysis', 'Geolocation SLA comparison':'comparisons'}
    with st.sidebar:
        st.image(laager_logo)
        st.markdown('---')
        st.title('You are welcome!')
        selected_menu = option_menu(None, options=[
            'SLA overview metrics', 'Geographic SLA analysis', 'Geolocation SLA comparison'
        ], default_index=0, orientation='vertical', menu_icon='menu-button-wide',
            styles={
        "container": {"padding": "0!important", "background-color": "#0C0431", "border-radius":"6px", "height":"300px", "font-weight":"bold", "family":"roboto"},
        "icon": {"color": "#F33309", "font-size": "25px"}, 
                                    "nav-link": {"font-size": "23px", "text-align": "left", "margin":"0px", "--hover-color": "##7FA6EB", "family":"roboto", "padding-top":"20px", "hover":"black"},
        "nav-link-selected": {"background-color": "#15E815"},
    }, icons=['bar-chart-line-fill', 'globe-americas', 'geo-alt-fill'])
    return 'views.' + map_app_tabs[selected_menu]
