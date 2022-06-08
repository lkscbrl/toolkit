# streamlit run C:\Users\lcabral\Desktop\Toolkit_de_diagnostico\toolkit\app.py

import streamlit as st
import data_upload_download, data_profiling, data_manipulation, data_visualization, analytics, mapping
#from PIL import Image


st.set_page_config(layout='wide', page_title='Assessment Toolkit', page_icon='🔎')
#image = Image.open('C:\\Users\\lcabral\\Desktop\\Toolkit_de_diagnostico\\logo.png')

st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

pages = {'Upload/Download Data':data_upload_download,
         'Mapping':mapping,
         'Data Profiling':data_profiling,
         'Data Manipulation':data_manipulation,
         'Data Visualization':data_visualization,
         'Analytics':analytics
        }

#st.sidebar.image(image)
st.sidebar.title('Assessment Toolkit')
selection = st.sidebar.selectbox('App Navigation', list(pages.keys()))
page = pages[selection]
        
if selection=='Upload/Download Data':
    sub_sessions = ['Upload Data', 'Inspect Data', 'Download Dataframe']
    select_df = False
    
elif selection=='Data Profiling':
    select_df = True
    
elif selection=='Data Manipulation':
    sub_sessions = ['New Column', 'Group By', 'Merge Datasets', 'Delete Columns',
                   'Missing Data', 'Replace Data', 'Filter Data', 'Split Column']
    select_df = True
    
elif selection=='Data Visualization':
    sub_sessions = ['View as Table', 'Plot Charts']
    select_df = True
    
elif selection=='Analytics':
    sub_sessions = ['Statistics', 'Crosstable', 'Pairplot', 'Pearson´s Correlation']
    select_df = True
    
elif selection=='Mapping':
    sub_sessions = ['Set Variables Types', 'Map Interest Variables']
    select_df = True

if select_df:
    
    try:
        st.session_state['select_df'] = st.sidebar.selectbox('Select Dataset:',
                                        list(st.session_state['dfs'].keys()))
        
    except:
        pass

try: 
    st.session_state['sub_session'] = st.sidebar.radio('Sub Session:', sub_sessions)
    
except:
    pass

page.app()