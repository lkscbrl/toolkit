import streamlit as st
import numpy as np
import plotly.express as px
import plotly.io as pio
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

pio.templates.default = 'seaborn'

def app():
    
    st.markdown('## Data Visualization')
    st.write('\n')
    
    try:
        select_df = st.session_state['select_df']
        df = st.session_state['dfs'][select_df]
        numeric_columns = df.columns[[x.kind in 'bifc' for x in np.array(df.dtypes)]]
        
    except:
        st.warning('Please load some data.')
        st.stop()
        pass
    
    try:
        
        if st.session_state['sub_session']=='Plot Charts':
            
            chart_types = ['Bars', 'Line', 'Scatter', 'Histogram', 'Boxplot']
            chart_type = st.selectbox('Chart type:', chart_types)
            
            c1, c2 = st.columns((3, 1))
            
            if chart_type=='Bars':
            
                agg_func = {'Sum':'sum', 'Mean':np.mean, 'Count':'count', 'Unique values': 'nunique'}
                
                with c2:
                    x_axis = st.selectbox('X axis:', list(df.columns))
                    y_axis = st.selectbox('Y axis:', numeric_columns)
                    legend = st.selectbox('Legend:', ['-'] + list(df.columns))
                    agg_by = st.selectbox('Aggregate:', agg_func.keys())
                    
                with c1:
                    
                    if legend!='-':
                        
                        tmp = df.groupby([x_axis, legend])[y_axis].agg(agg_func[agg_by]).reset_index()
                        fig = px.bar(tmp, x=x_axis, y=y_axis, color=legend)
                        fig.update_layout(autosize=True, title_text=f'{y_axis} per {x_axis} and {legend}', template='simple_white')
                        
                    else:
                        tmp = df.groupby(x_axis)[y_axis].agg(agg_func[agg_by]).reset_index()
                        fig = px.bar(tmp, x=x_axis, y=y_axis)
                        fig.update_layout(autosize=True, title_text=f'{y_axis} by {x_axis}')
                        
                    fig.update_yaxes(automargin=True)
                    st.plotly_chart(fig, use_container_width=True)   
                    
            if chart_type=='Line':
            
                agg_func = {'Sum':'sum', 'Mean':np.mean, 'Count':'count', 'Unique values': 'nunique'}
                
                with c2:
                    x_axis = st.selectbox('X axis:', list(df.columns))
                    y_axis = st.selectbox('Y axis:', numeric_columns)
                    legend = st.selectbox('Legend:', ['-'] + list(df.columns))
                    agg_by = st.selectbox('Aggregate:', agg_func.keys())
                    
                with c1:
                    
                    if legend!='-':
                        
                        tmp = df.groupby([x_axis, legend])[y_axis].agg(agg_func[agg_by]).reset_index()
                        fig = px.line(tmp, x=x_axis, y=y_axis, color=legend)
                        fig.update_layout(autosize=True, title_text=f'{y_axis} by {x_axis} and {legend}')
                        
                    else:
                        tmp = df.groupby(x_axis)[y_axis].agg(agg_func[agg_by]).reset_index()
                        fig = px.line(tmp, x=x_axis, y=y_axis)
                        fig.update_layout(autosize=True, title_text=f'{y_axis} by {x_axis}')
                        
                    fig.update_yaxes(automargin=True)
                    st.plotly_chart(fig, use_container_width=True)    
                    
            if chart_type=='Scatter':
            
                with c2:
                    x_axis = st.selectbox('X axis:', numeric_columns)
                    y_axis = st.selectbox('Y axis:', numeric_columns)
                    legend = st.selectbox('Legend:', ['-'] + list(df.columns))
                    
                with c1:
                    
                    if legend!='-':
                        
                        tmp = df[[x_axis, y_axis, legend]]
                        fig = px.scatter(tmp, x=x_axis, y=y_axis, color=legend)
                        fig.update_layout(autosize=True, title_text=f'{y_axis} by {x_axis} and {legend}')
                        
                    else:
                        tmp = tmp = df[[x_axis, y_axis]]
                        fig = px.scatter(tmp, x=x_axis, y=y_axis)
                        fig.update_layout(autosize=True, title_text=f'{y_axis} by {x_axis}')
                        
                    fig.update_yaxes(automargin=True)
                    st.plotly_chart(fig, use_container_width=True) 
    
            if chart_type=='Boxplot':
            
                with c2:
                    y_axis = st.selectbox('Y axis:', numeric_columns)
                    x_axis = st.selectbox('X axis:', ['-'] + list(df.columns))
                    
                with c1:
                    
                    if x_axis!='-':
                        
                        tmp = df[[x_axis, y_axis]]
                        fig = px.box(tmp, x=x_axis, y=y_axis)
                        fig.update_layout(autosize=True, title_text=f'{y_axis} by {x_axis}')
                        
                    else:
                        tmp = df[y_axis]
                        fig = px.box(tmp, y=y_axis)
                        fig.update_layout(autosize=True, title_text=f'{y_axis}')
                        
                    fig.update_yaxes(automargin=True)
                    st.plotly_chart(fig, use_container_width=True) 
                    
            if chart_type=='Histogram':
            
                with c2:
                    x_axis = st.selectbox('X axis:', list(df.columns))
                    legend = st.selectbox('Legend:', ['-'] + list(df.columns))
                    bins = st.number_input('Bins', min_value=1, max_value=100, value=10, step=1)
                    
                with c1:
                    
                    if legend!='-':
                        
                        tmp = df[[x_axis, legend]]
                        fig = px.histogram(tmp, x=x_axis, color=legend, nbins=bins)
                        fig.update_layout(autosize=True, title_text=f'{x_axis} by {legend}')
                        
                    else:
                        tmp = df[x_axis]
                        fig = px.histogram(tmp, x=x_axis, nbins=bins)
                        fig.update_layout(autosize=True, title_text=f'{x_axis}')
                            
                    fig.update_yaxes(automargin=True)
                    st.plotly_chart(fig, use_container_width=True)
                    
        elif st.session_state['sub_session']=='View as Table':
            
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_pagination()
            gb.configure_side_bar(filters_panel=True, columns_panel=False)
            gb.configure_default_column(groupable=False, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
            gridOptions = gb.build()

            AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=True, height=600) # allow_unsafe_jscode=True, update_mode=GridUpdateMode.FILTERING_CHANGED 
                    
    except:
        st.error('Please select the correct parameters for the selected chart type and aggregation function.')