import streamlit as st
import io

def app():
    
    st.markdown(f'## {st.session_state["sub_session"]}')
    st.write('\n')
    
    try:
        
        select_df = st.session_state['select_df']
        df = st.session_state['dfs'][select_df]
        
    except:
        st.warning('Please load some data.')
        st.stop()
        pass
    
    try:
        
        if st.session_state['sub_session']=='Set Variables Types':
            
            st.write(df.head())
            
            type_dict = {'Integer':'int', 'Decimal':'float', 'Text':'str', 'Date':'datetime64[ns]'}
            
            c1, c2 = st.columns((4, 1))
            
            with c1:
                select_cols = st.multiselect('Select columns:', df.columns)
                
            with c2:
                select_type = st.selectbox('Select type:', type_dict.keys())
                
            set_type = st.button('Set type')
            
            if set_type and select_cols:
                
                df[select_cols] = df[select_cols].astype(type_dict[select_type])                
                st.session_state['dfs'][select_df] = df
                
            data_info = st.expander(label='Data info')
            
            with data_info:
                buffer = io.StringIO()
                df.info(buf=buffer)
                s = buffer.getvalue()
                st.text(s)
            
        elif st.session_state['sub_session']=='Map Interest Variables':
        
            cols = ['-'] + list(df.columns)
            
            variables = ['origin', 'destiny', 'distance in kilometers', 'quantity', 'weight',
                 'freight', 'shipment date', 'arrival date', 'value']
    
            for idx in range(len(variables)):
                st.selectbox(variables[idx], cols, key=idx)
                
            save = st.button('Save mapping')
                
            if save:
                st.success('Mapping completed successfully.')
        
    except Exception as e:
        st.error(e)
        pass