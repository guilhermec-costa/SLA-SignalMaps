import streamlit as st
from typing import Union, List
import pandas as pd
from streamlit.connections import SQLConnection


class Queries:
    def __init__(self, name:str) -> None:
        self.all_queries_commands = []
        self.all_queries_names = []
        self.results = {}
        
        # imprescendível definir o nome da conexão antes de iniciar a conexão
        self.name = name
        self.connection = self.start_connection()
    
    def __repr__(self) -> str:
        return 'Queries()'
    
    def __str__(self) -> str:
        return 'An instance of "Queries". It is probably something about {}'.format(self.name)

    def add_queries(self, const_list: List) -> None:
        for constant in const_list:
            self.all_queries_commands.append(constant[0])
            self.all_queries_names.append(constant[1])
    
    def get_query_result(self):
        return self.results

    def show_queries(self):
        st.write(self.all_queries_commands)
        
    def get_name(self):
        return self.name

    @st.cache_data(ttl=36000)
    def run_queries(_self, query_commands):
        for query_name_index, query in enumerate(query_commands):
            _self.results[_self.all_queries_names[query_name_index]] = _self.connection.query(sql=query, params={'name':'Business Unit'})
        return _self.results
    
    @st.cache_data(ttl=36000)
    def run_single_query(_self, command:str) -> None:
        st.write(command)
        return _self.connection.query(sql=command)

    def verify_connection(self) -> Union[str, bool]:
        return 'success' if self.connection is not None else False
    
    @st.cache_data
    def load_imporant_data(queries_responses, specific_response:str) -> pd.DataFrame:
        return pd.DataFrame(queries_responses[specific_response])
    
    @st.cache_resource(ttl=36000)
    def start_connection(_self):
        #st.write(_self.name)
        try:
            return st.experimental_connection(name=_self.name, ttl=1200, type=SQLConnection)
        except Exception:
            st.error('Failed to connect to database.')
        return None
        
