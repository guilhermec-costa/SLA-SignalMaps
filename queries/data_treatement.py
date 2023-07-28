import pandas as pd
import streamlit as st

def clear_dataframe(data:pd.DataFrame, col_subset:str, vl_to_exclude:str) -> None:
     return data[~(data[col_subset] == vl_to_exclude)]

@st.cache_data
def read_data(name:str, sep: str = ',') -> pd.DataFrame:
    return pd.read_csv(name, sep=sep)
