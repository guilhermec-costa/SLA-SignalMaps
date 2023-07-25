import streamlit as st
from typing import List, Tuple, Any

def initialize_session_states(params:List[Tuple[str, Any]]):
    for tuples in params:
        if str(tuples[0]) not in st.session_state:
            st.session_state[str(tuples[0])] = tuples[1]