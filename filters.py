# all available filters (dashboards)
import streamlit as st
import pandas as pd

style_markdown_warning = """
color: rgb(255, 255, 194);
background-color: rgba(255, 227, 18, 0.2);
border-radius: 5px;
height: 55px;
display: flex;
align-items: center;
vertical-align: middle;
padding-left: 14px;
margin: 4px;
"""
style_markdown_error = """
color: rgb(255, 222, 222);
background-color: rgba(255, 108, 108, 0.2);
border-radius: 5px;
height: 55px;
display: flex;
align-items: center;
vertical-align: middle;
padding-left: 14px;
margin: 4px;
"""

class Filters:

    def __init__(self, data_frame: pd.DataFrame) -> None:
        self.df = data_frame
        self.c1_date, self.c2_date = st.columns(2)
    
    def __str__(self) -> str:
        return 'Objeto DataFrame que pode ser filtrado'
    
    def __repr__(self) -> str:
        return 'Filters(pandas.DataFrame())'
    
    def validate_filter(self, filter_name:str, opcs:list = None, refer_column:str =None) -> None:
        apply_filter = getattr(self, filter_name)
        if len(opcs) >= 1: 
            filtered_dataframe = apply_filter(opcs, refer_column)

    def general_filter(self, opcs: list, refer_column):
        self.df = self.df[(self.df[refer_column].isin(opcs))]
    
    def general_qty_filter(self, min_value, max_value, refer_column):
        self.df = self.df[(self.df[refer_column] >= min_value) & (self.df[refer_column] <= max_value)]

    
