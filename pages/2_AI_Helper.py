import streamlit as st
import pandas as pd


print('...........in AI helper ..............')
print (st.session_state.uploaded_file) 

if 'column_mapping_status' not in st.session_state or not st.session_state.column_mapping_status:
    st.error('Please generate ARR metrics')
else:
    st.write('AI to your help')




print('........... end of  visualize..............')