import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from math import log, floor
import seaborn as sns
import matplotlib.pyplot as plt

pio.templates.default = 'none'
sns.set_theme()

def human_format(number):
    units = ['', 'K', 'M', 'G', 'T', 'P']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return '%.2f%s' % (number / k**magnitude, units[magnitude])

def app():
    st.markdown(f'## {st.session_state["sub_session"]}')
    st.write('\n')
    
    try:
        select_df = st.session_state['select_df']
        df = st.session_state['dfs'][select_df]
        numeric_columns = df.columns[[x.kind in 'bifc' for x in np.array(df.dtypes)]]
        
    except:
        st.warning('Please load some data.')
        st.stop()
        pass
    
    if st.session_state['sub_session']=='Statistics':
        
        try:
            
            col = st.selectbox('Select column:', numeric_columns)
            
            serie = df[col].fillna(0).values.flatten().copy()
            
            c11, c12 = st.columns(2)
            
            with c11:
                how = st.radio('Threshold:', ('Mean', 'Median', 'Custom'))
                #st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
                
            with c12:
                if how=='Custom':
                    ct = st.number_input('Custom value', min_value=1, value=10)
            
            if how=='Mean':
                threshold = np.mean(serie)
                
            elif how=='Median': 
                threshold = np.median(serie)
                
            elif how=='Custom': 
                threshold = ct
                
            total = serie.sum()
            bottom = serie[serie<=threshold].sum()
            top = serie[serie>=threshold].sum()
            
            increase = serie.copy()
            increase[increase<=threshold] = threshold
            increase = increase.sum()
            
            decrease = serie.copy()
            decrease[decrease>=threshold] = threshold
            decrease = decrease.sum()
            
            
            c1, c2, c3 = st.columns(3)
            c4, c5, c6 = st.columns(3)
            
            with c1:
                st.metric(label='Total', value=human_format(total), delta_color='off')
                
            with c4:
                st.metric(label='Threshold', value=human_format(threshold), delta_color='off')
                
            with c2:
                st.metric(label='Total under the threshold', value=human_format(bottom), delta_color='off',
                          delta='{0:.2f}%'.format(bottom/total*100))
                
            with c5:
                st.metric(label='Total above the threshold', value=human_format(top), delta_color='off',
                          delta='{0:.2f}%'.format(top/total*100))
            
            with c3:
                st.metric(label='Adjust up', value=human_format(increase),
                          delta='{0:.2f}%'.format(100*((increase/total)-1)))
            
            with c6:
                st.metric(label='Adjust down', value=human_format(decrease), delta_color='inverse',
                          delta='{0:.2f}%'.format(100*((decrease/total)-1)))
            
            
            c7, c8 = st.columns((1,3))
            
            with c7:
                st.dataframe(pd.DataFrame(serie).describe().rename(columns={0:'Statistics'}))
                
            with c8:
                fig = px.histogram(serie, marginal='box', histnorm='probability density', height=295)
                fig.add_vline(x=threshold, line_dash='dash', line_color='black')
                fig.update_yaxes(side='right')
                fig.update_layout(showlegend=False, xaxis_title=col, yaxis_title='Probability Density',
                                  margin=dict(l=0, r=50, t=8, b=50))
                
                #fig.write_image('fig.png')
                #st.image('fig.png', use_column_width='always')
                
                st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(e)
            pass
        
    if st.session_state['sub_session']=='Crosstable':
        
        try:
            
            c1, c2 = st.columns(2)

            with c1:
                col1 = st.selectbox('First Column:', df.columns, key=1)
             
            with c2:
                col2 = st.selectbox('Second Column:', df.columns, key=2)
                
            serie1 = df[col1].copy()
            serie2 = df[col2].copy()
                
            if serie1.nunique() < serie2.nunique():
                serie2, serie1 = serie1, serie2
                
            how = st.radio('Show as:', ('Absolut values', 'Percentage of total',
                                        'Percentage of rows', 'Percentage of columns'))
            
            if how == 'Absolut values':
                norm = False
            
            elif how == 'Percentage of total':
                norm = True
            
            elif how == 'Percentage of rows':
                norm = 'index'
                
            elif how == 'Percentage of columns':
                norm = 'columns'
             
            st.table(pd.crosstab(serie1, serie2, normalize=norm).style.background_gradient(axis=None))

        except Exception as e:
            st.error(e)
            pass
        
    if st.session_state['sub_session']=='Pairplot':
           
        try:
            
            col = st.multiselect('Select columns:', numeric_columns)
            hue = st.selectbox('Legend:', ['-'] + list(df.columns))
            
            if hue=='-':
                leg=None
                
            else:
                leg=hue 
                col.append(hue)
                
            fig = sns.pairplot(df[col], hue=leg)
            fig.savefig('fig.png')
            st.image('fig.png', use_column_width='auto')
            #st.pyplot(fig)

        except Exception as e:
            st.error(e)
            pass
        
    if st.session_state['sub_session']=='Pearson´s Correlation':
        
        try:

            col = st.multiselect('Select columns:', numeric_columns)
            fig, ax = plt.subplots()
            sns.heatmap(df[col].corr(), ax=ax, annot=True, cbar=False, vmin=-1, vmax=1, cmap='vlag')
            st.write(fig)
            
        except Exception as e:
            st.error(e)
            pass