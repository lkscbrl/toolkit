import streamlit as st
from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

def app():
    st.markdown('## Data Profiling')
    st.write('\n')
    
    try:
        
        load_profile = st.button('Load Profiling')
        
        if load_profile:
            
            st.session_state['profile'] = ProfileReport(st.session_state['dfs'][st.session_state['select_df']], minimal=True)
            st_profile_report(st.session_state['profile'])
            
    except:
        pass