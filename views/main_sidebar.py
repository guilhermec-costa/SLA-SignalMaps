from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu
# from rembg import remove

module_mapping = {'views.sla_overview':'sla_overview',
                    'views.geospacial_analysis':'geo_analysis'
                }

def main_sidebar() -> str:
    laager_logo = Image.open('logos/logo_laager.jpg')
    # output_image = 'logos/logo_laager_nobg.jpg'
    # output = remove(laager_logo)
    # output.save(output_image)
    map_app_tabs = {'SLA overview metrics': 'sla_overview', 'Geographic SLA analysis': 'geospacial_analysis'}
    with st.sidebar:
        st.title('Your welcome!')
        selected_menu = option_menu('Dashboards Laager', options=[
            'SLA overview metrics', 'Geographic SLA analysis'
        ], default_index=0, orientation='vertical', menu_icon='menu-button-wide',
            styles={
        "container": {"padding": "0!important", "background-color": "#0E1117", "border-radius":"6px", "height":"300px", "font-weight":"bold"},
        "icon": {"color": "#13CF29", "font-size": "25px"}, 
        "nav-link": {"font-size": "23px", "text-align": "left", "margin":"0px", "--hover-color": "##7FA6EB", "font-family":"roboto", "padding-top":"20px"},
        "nav-link-selected": {"background-color": "#7CC7FF"},
    }, icons=['bar-chart', 'map'])
    return 'views.' + map_app_tabs[selected_menu]