import streamlit as st
import pandas as pd

@st.cache_data
def read_data(name:str, sep: str = ',') -> pd.DataFrame:
    return pd.read_csv(name, sep=sep)