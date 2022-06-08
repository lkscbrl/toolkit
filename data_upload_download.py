import streamlit as st
import pandas as pd
import snappy
import fastparquet
from unidecode import unidecode
import time
import string
from io import BytesIO
import itertools
from pyxlsb import open_workbook as open_xlsb


st.session_state['dfs'] = dict()

def end_time(start):
    
    end = time.time()
    
    return f'Data compilation finished in {round(end-start, 0)} seconds.'

def remove_punctuation(text): 

  translator = str.maketrans('', '', string.punctuation)

  return text.translate(translator) 

def remove_accented_chars(text):
  
  text = unidecode(text)
  
  return text

def remove_white_spaces(x):
    
    return '_'.join(x.lower().split())

def clear_text(x):
    
    return remove_white_spaces(remove_punctuation(remove_accented_chars(x)))

def to_excel(df):
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    
    return processed_data

def app():
    
    st.markdown(f'## {st.session_state["sub_session"]}')
    st.write('\n')

    if st.session_state['sub_session']=='Upload Data':
        
        dataset_type = st.radio('Dataset Type:', ('Combine Multiple Excel Files', 'Combine Multiple CSV Files', 'Parquet File'), key=17,
                                help='Select mutiples excel files or a parquet file previously downloaded.')
    
        try:
            
            if dataset_type == 'Parquet File':
                
                dataset_pqt = st.file_uploader('Select a dataset to upload', accept_multiple_files=False)
                df_name_pqt = st.text_input('Load as:', key=18)
                load_pqt = st.button('Load Dataset')
                
                if load_pqt:
                    
                    if dataset_pqt and df_name_pqt:
                        
                        start = time.time()
                        
                        st.session_state['dfs'][df_name_pqt] = pd.read_parquet(dataset_pqt)
                        
                        st.success(end_time(start))
                        
            elif dataset_type == 'Combine Multiple Excel Files':
            
                xlsx_files = st.file_uploader('Select a dataset to upload', accept_multiple_files=True, type = ['xlsx', 'xlsm'])
                
                c1, c2 = st.columns((3, 1))
                
                with c1:
                    
                    try:
                        
                        sheet_name = list()

                        for f in xlsx_files:
                            sheet_name.append(pd.ExcelFile(f).sheet_names)
                        
                        sheet_name = list(set(itertools.chain(*sheet_name)))
                        
                        sheet = st.multiselect('Select sheet:', sheet_name)
                        
                    except Exception as e:
                        st.error(e)
                        pass
            
                    
                with c2:
                    skip_rows = st.number_input('Skip rows', min_value=0, max_value=100, value=0, step=1,
                                                help='Number of rows you wat to skip. Sometimes there are rows above the table header.')
                
                df_name_xlsx = st.text_input('Load as:', key=1, help='The name that will be mentioned in every analysis.')
                
                load_files = st.button('Load Files')
                
                if load_files and sheet and df_name_xlsx:
                    
                    start = time.time()
                    
                    df = list()
                        
                    for f in xlsx_files:
                        st.write(f)
                        for s in sheet:
                            
                            try:
                                tmp = pd.read_excel(f, sheet_name=s, skiprows=skip_rows)
                            
                                #tmp = pd.read_excel(f, sheet_name=s, skiprows=skip_rows, dtype=str)
                                
                                cols = tmp.columns
                                new_cols = [clear_text(c) for c in cols]
                                rmap = dict(zip(cols, new_cols))
                                tmp = tmp.rename(columns=rmap)
            
                                df.append(tmp)
                            except:
                                pass
                                
                    
                    df = pd.concat(df, ignore_index=True)
                    
                    drop_cols = df.isnull().mean().reset_index()
                    drop_cols = list(drop_cols.loc[drop_cols[0] == 1]['index'])
                    df.drop(columns=drop_cols, inplace=True)

                    st.session_state['dfs'][df_name_xlsx] = df
                    
                    st.success(end_time(start))
                    
            elif dataset_type == 'Combine Multiple CSV Files':
                
                csv_files = st.file_uploader('Select a dataset to upload', accept_multiple_files=True, type = ['csv'])
                
                c1, c2 = st.columns((3, 1))
                c3, c4, c5, c6 = st.columns(4)
                
                with c1:
                    df_name_csv = st.text_input('Load as:', key=1, help='The name that will be mentioned in every analysis.')
                
                with c2:
                    skip_rows = st.number_input('Skip rows', min_value=0, max_value=100, value=0, step=1,
                                                help='Number of rows you wat to skip. Sometimes there are rows above the table header.')
                
                with c3:
                    sep = st.text_input('Delimiter:', value=';', key=2)
                    
                with c4:
                    dec = st.text_input('Decimal:', value=',', key=3)
                    
                with c5:
                    tho = st.text_input('thousands:', value='.', key=4)
                        
                with c6:
                    cod = st.selectbox('Select encoding:', ['utf-8', 'ISO-8859-1'])
                    
                load_files = st.button('Load Files')
                
                if load_files and csv_files and df_name_csv and sep and dec and tho:
                    
                    start = time.time()
                    
                    df = list()
                        
                    for f in csv_files:
                        
                        tmp = pd.read_csv(f, skiprows=skip_rows, sep=sep, encoding=cod, thousands=tho,
                                          decimal=dec, low_memory=False)
                        cols = tmp.columns
                        new_cols = [clear_text(c) for c in cols]
                        rmap = dict(zip(cols, new_cols))
                        tmp = tmp.rename(columns=rmap)
    
                        df.append(tmp)
                    
                    df = pd.concat(df)
                    
                    drop_cols = df.isnull().mean().reset_index()
                    drop_cols = list(drop_cols.loc[drop_cols[0] == 1]['index'])
                    df.drop(columns=drop_cols, inplace=True)

                    st.session_state['dfs'][df_name_csv] = df
                    
                    st.success(end_time(start))
                    
        except Exception as e:
            st.error(e)
            pass         

    elif st.session_state['sub_session']=='Inspect Data':
        
        try:
            
            c1, c2, c3 = st.columns((2, 1, 1))
            
            with c1:
                inspect_df = st.selectbox('Select Dataset:', list(st.session_state['dfs'].keys()))
            
            with c2:
                n_rows = int(st.number_input('Rows', min_value=5, max_value=1000, value=5, step=10))
            
            with c3:
                head_tail = st.radio('View:', ('Top Rows', 'Bottom Rows'))
            
            if inspect_df:
            
                if head_tail=='Top Rows':
                    st.dataframe(st.session_state['dfs'][inspect_df].head(n_rows))
                
                else:
                    st.dataframe(st.session_state['dfs'][inspect_df].tail(n_rows))
                                 
        except Exception as e:
            st.warning(e)
            st.stop() 

    elif st.session_state['sub_session']=='Download Dataframe':
    
        try:

            persist_df = st.selectbox('Select Dataset:', list(st.session_state['dfs'].keys()), key=13)

            if persist_df:

                df_xlsx = to_excel(st.session_state['dfs'][persist_df])
                
                st.download_button(label='📥 Download xlsx',
                                data=df_xlsx ,
                                file_name= 'dataset.xlsx')

        except:
            st.warning('Please load some data.')
            st.stop()
            pass
        