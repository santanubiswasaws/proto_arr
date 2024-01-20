import streamlit as st
import pandas as pd

from arr_lib.styling import BUTTON_STYLE
from arr_lib.styling import MARKDOWN_STYLES
from arr_lib.styling import GLOBAL_STYLING

st.markdown(BUTTON_STYLE, unsafe_allow_html=True)
st.markdown(MARKDOWN_STYLES, unsafe_allow_html=True)
st.markdown(GLOBAL_STYLING, unsafe_allow_html=True)


print('...........in AI helper ..............')
print (st.session_state.uploaded_file) 

if 'column_mapping_status' not in st.session_state or not st.session_state.column_mapping_status:
    st.error('Please generate ARR metrics')
else:
    st.write('AI to your help')




print('........... end of  visualize..............')