import streamlit as st
from typing import Union, List
import pandas as pd

class Queries:
    def __init__(self, name:str) -> None:
        self.all_queries_commands = []
        self.all_queries_names = []
        self.results = {}
        self.connection = Connection.start_connection()
    
    def __repr__(self) -> str:
        return 'Queries()'

    def add_queries(self, const_list: List) -> None:
        for constant in const_list:
            self.all_queries_commands.append(constant[0])
            self.all_queries_names.append(constant[1])
    
    def get_query_result(self):
        return self.results

    def show_queries(self):
        st.write(self.all_queries_commands)

    @st.cache_data(ttl=36000)
    def run_queries(_self, query_commands):
        for query_name_index, query in enumerate(query_commands):
            _self.results[_self.all_queries_names[query_name_index]] = _self.connection.query(sql=query, params={'name':'Business Unit'})
        return _self.results

    def verify_connection(self) -> Union[str, bool]:
        return 'success' if self.connection is not None else False
    
    @st.cache_data
    def load_imporant_data(queries_responses, specific_response:str) -> pd.DataFrame:
        return pd.DataFrame(queries_responses.get(specific_response))

class Connection:
    @st.cache_resource
    def start_connection():
        try:
            return st.experimental_connection(name='mysql', ttl=1200, type='sql')
        except Exception:
            st.error('Failed to connect to database.')
            raise
            return None
        
