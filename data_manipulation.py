import streamlit as st
import pandas as pd
import pandasql as ps
import numpy as np
from unidecode import unidecode
import string


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

def merge_dict(dict1, dict2):
    
    try:
        dict3 = {**dict1, **dict2}
        for key, value in dict3.items():
           if key in dict1 and key in dict2:
                   dict3[key] = [value , dict1[key]]
                   
        return dict3
    except:
        return dict2

def app():
    
    st.markdown(f'## {st.session_state["sub_session"]}')
    st.write('\n')
    
    try:
        select_df = st.session_state['select_df']
        
    except:
        st.warning('Please load some data.')
        st.stop()
        pass
    
    if st.session_state['sub_session']=='New Column':
        
        try:
    
            measure_name = st.text_input('New column name:', key=55)
            measure = st.text_input('Formula:', key=56,
                                    help='I.E. column1/column2, column3+column4, etc.')
            add_measure = st.button('Add')
            
            if add_measure:          
                    
                temp = st.session_state['dfs'][select_df].copy()
                q = f'SELECT {measure} FROM temp'
                res = ps.sqldf(q, locals())
                
                if len(res)==1:
                    res = res.unstack()[0]
        
                st.session_state['dfs'][select_df][clear_text(measure_name)] = res 
                
            st.write(st.session_state['dfs'][select_df].head())
            
        except Exception as e:
            st.error(e)
            pass
        
    elif st.session_state['sub_session']=='Group By':
        
        try:
    
            group_cols = st.multiselect('Group by:', st.session_state['dfs'][select_df].columns, key=57,
                                        help='Similar to a pivot table, select all the columns you want to see as rows.')
            sum_cols = st.multiselect('Sum:', st.session_state['dfs'][select_df].columns, key=58)
            mean_cols = st.multiselect('Mean:', st.session_state['dfs'][select_df].columns, key=59)
            count_cols = st.multiselect('Count rows:', st.session_state['dfs'][select_df].columns, key=60)
            unique_cols = st.multiselect('Count unique values:', st.session_state['dfs'][select_df].columns, key=61)
            df_name = st.text_input('New dataframe name:', key=65)
            group_df = st.button('Group Dataframe')
            
            if group_df and df_name and(sum_cols or mean_cols or count_cols or unique_cols):
                
                operations = [{x:'sum'} for x in sum_cols] +\
                             [{x:np.mean} for x in mean_cols] +\
                             [{x:'count'} for x in count_cols] +\
                             [{x:'nunique'} for x in unique_cols]
                             
                agg_func = dict()
                
                for o in operations:
                    agg_func = merge_dict(agg_func, o)
                
                temp = st.session_state['dfs'][select_df].groupby(group_cols).agg(agg_func).reset_index()
                temp.columns = ['_'.join(x).rstrip('_') if type(x) is tuple else x for x in temp.columns]
                
                st.write(temp.head())
                st.session_state['dfs'][df_name] = temp
                    
        except Exception as e:
            st.error(e)
            pass
        
                    
    elif st.session_state['sub_session']=='Merge Datasets':
        
        try:
    
            right_df = st.selectbox('Dataset to search', list(st.session_state['dfs'].keys()))
            
            c1, c2 = st.columns(2)
            
            with c1:
                left_on = st.selectbox('Origin key:', list(st.session_state['dfs'][select_df].columns),
                                       help='Values to search for.')
                
            with c2:
                right_on = st.selectbox('Destiny key', list(st.session_state['dfs'][right_df].columns),
                                        help='Where to search values.')
            
            how = st.radio('How:', ('Bring values with matching keys', 'Bring values that appears in both dataframes only'))
            how_2 = {'Bring values with matching keys':'left', 'Bring values that appears in both dataframes only':'inner'}
            new_df = st.radio('Create new dataframe?', ('No', 'Yes'))
            
            if new_df=='Yes':
                new_df_name = st.text_input('Dataset name:', key=2)
                
            merge_button = st.button('Merge Dataset')
            
            if merge_button:
                
                if right_df and left_on and right_on:
                    
                    if new_df=='Yes' and new_df_name:
                        st.session_state['dfs'][new_df_name] = st.session_state['dfs'][select_df].merge(st.session_state['dfs'][right_df], how=how_2[how],
                                                                             left_on=left_on, right_on=right_on)
                        st.write(st.session_state['dfs'][new_df_name].head())
                    else:
                        st.session_state['dfs'][select_df] = st.session_state['dfs'][select_df].merge(st.session_state['dfs'][right_df], how=how_2[how],
                                                                             left_on=left_on, right_on=right_on)
                        st.write(st.session_state['dfs'][select_df].head())
               
        except Exception as e:
            st.error(e)
            pass

    elif st.session_state['sub_session']=='Delete Columns':   
            
        try:
            
            columns = st.multiselect('Select Columns to Delete:', st.session_state['dfs'][select_df].columns)
            drop_bt = st.button('Delete Columns')
            
            if drop_bt:
                st.session_state['dfs'][select_df] = st.session_state['dfs'][select_df].drop(columns=columns)
            
            st.write(st.session_state['dfs'][select_df].head())
            
        except Exception as e:
            st.error(e)
            pass
            
    elif st.session_state['sub_session']=='Missing Data':
    
        try:
            
            columns = st.multiselect('Select Columns to Check for Missing Values:', st.session_state['dfs'][select_df].columns)
            
            c1, c2 = st.columns(2)
            
            with c1:
                op = st.radio('Operation:', ('Fill Missing Values', 'Delete Rows'))
            
            if op=='Fill Missing Values':
                
                with c2:
                    op_2 = st.radio('Fill With:', ('zero', 'mean', 'median', 'mode'))
                    
                fill_bt = st.button('Fill Values')
                
                if fill_bt and columns:
                    
                    for c in columns:
                        
                        if op_2=='zero':
                            st.session_state['dfs'][select_df][c].fillna(0, inplace=True)
                            
                        elif op_2=='mean':
                            st.session_state['dfs'][select_df][c].fillna(st.session_state['dfs'][select_df][c].mean(), inplace=True)
                        
                        elif op_2=='median':
                            st.session_state['dfs'][select_df][c].fillna(st.session_state['dfs'][select_df][c].median(), inplace=True)
                            
                        elif op_2=='mode':
                            st.session_state['dfs'][select_df][c].fillna(st.session_state['dfs'][select_df][c].mode(), inplace=True)
                            
            if op=='Delete Rows':
                drop_null_bt = st.button('Delete Rows')
                
                if drop_null_bt and columns:
                    
                    st.session_state['dfs'][select_df].dropna(subset=columns, inplace=True)
        
            st.write(st.session_state['dfs'][select_df].head())
                        
        except Exception as e:
            st.error(e)
            pass
            
    elif st.session_state['sub_session']=='Replace Data':
    
        try:
            
            columns = st.multiselect('Select Columns to Replace Values:',
                                     st.session_state['dfs'][select_df].columns)
            
            c1, c2 = st.columns(2)
            
            with c1:
                replace_from = st.text_input('Replace from:', key=6)
                
            with c2:    
                replace_to = st.text_input('Replace to:', key=7)

            replace_bt = st.button('Replace Values')

            if replace_bt and replace_from and replace_to:

                for c in columns:

                    st.session_state['dfs'][select_df][c].replace(replace_from, replace_to, inplace=True)
            
            st.write(st.session_state['dfs'][select_df].head())
            
        except Exception as e:
            st.error(e)
            pass
     
    elif st.session_state['sub_session']=='Filter Data':
    
        try:
            
            sql_filter = st.text_input('Filter condition:',
                                       help='I.E. column1<=150, column2=="São Paulo", etc.')
            new_filter_df = st.radio('Create new dataframe? ', ('Yes', 'No'))

            if new_filter_df=='Yes':
                new_filter_df_name = st.text_input('New dataset name:')

            filter_bt = st.button('Filter Data')

            if filter_bt and sql_filter:

                if new_filter_df:
                    st.session_state['dfs'][new_filter_df_name] = st.session_state['dfs'][select_df].query(sql_filter).copy()

                else:
                    st.session_state['dfs'][select_df] = st.session_state['dfs'][select_df].query(sql_filter).copy()
            
            st.write(st.session_state['dfs'][select_df].head())
             
        except Exception as e:
            st.error(e)
            pass
        
    elif st.session_state['sub_session']=='Split Column':
    
        try:
            
            select_col = st.selectbox('Select column', list(st.session_state['dfs'][select_df].columns),
                                    help='Select column to split extract data.')
            delimiter = st.text_input('Delimiter:')
            
            how_dict = {'Before delimiter':0, 'After delimiter':-1}
            
            how = st.radio('How:', how_dict.keys())
            
            split_bt = st.button('Split Column')
            
            if split_bt and delimiter:
                
                st.session_state['dfs'][select_df][select_col] = st.session_state['dfs'][select_df][select_col].str.split(delimiter).str[how_dict[how]]
            
            st.write(st.session_state['dfs'][select_df].head())
            
        except Exception as e:
            st.error(e)
            pass
         