import streamlit as st

def update_fig_layouts(figs, theme):
    for fig in figs:
        fig.update_layout(mapbox=dict(accesstoken=st.secrets.mapbox.mapbox_token, style=theme))