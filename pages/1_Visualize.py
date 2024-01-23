import streamlit as st
import pandas as pd
import altair as alt

from arr_lib.styling import BUTTON_STYLE
from arr_lib.styling import MARKDOWN_STYLES
from arr_lib.styling import GLOBAL_STYLING

import arr_lib.arr_charts as ac

st.markdown(BUTTON_STYLE, unsafe_allow_html=True)
st.markdown(MARKDOWN_STYLES, unsafe_allow_html=True)
st.markdown(GLOBAL_STYLING, unsafe_allow_html=True)

st.header("Visualize ARR Data")
st.markdown("<br>", unsafe_allow_html=True)

if 'metrics_df' not in st.session_state: 
    metrics_df = pd.DataFrame()
else:
    # copy uploaded ARR metrics from session 
    metrics_df = st.session_state.metrics_df.copy()
    customer_arr_waterfall_df = st.session_state.customer_arr_waterfall_df.copy()
    customer_arr_df = st.session_state.customer_arr_df.copy()
    logo_metrics_df = st.session_state.logo_metrics_df.copy()

if 'replan_metrics_df' not in st.session_state: 
    replan_metrics_df = pd.DataFrame()
else: 
    # copy adjusted ARR metrics from session 
    replan_metrics_df = st.session_state.replan_metrics_df.copy()
    replan_customer_arr_waterfall_df = st.session_state.replan_customer_arr_waterfall_df.copy()
    replan_customer_arr_df = st.session_state.replan_customer_arr_df.copy()
    replan_logo_metrics_df = st.session_state.replan_logo_metrics_df.copy()

if (metrics_df.empty or replan_metrics_df.empty): 
    st.error('Please generate ARR metrics')
    st.stop()


##
## ARR Analytics 
##
st.subheader('ARR Trends')
arr_tab1, arr_tab2= st.tabs(["Final Adjusted ARR", "Uploaded ARR"])
with arr_tab1: 

    st.markdown("<br>", unsafe_allow_html=True)
    arr_result = ac.arr_walk_chart(replan_metrics_df, '#88b988', 'Final Adjusted ARR')
    st.altair_chart(arr_result, theme="streamlit", use_container_width=False)

with arr_tab2: 

    st.markdown("<br>", unsafe_allow_html=True)
    upld_arr_result = ac.arr_walk_chart(metrics_df, '#77aaca', 'Uploaded ARR')
    st.altair_chart(upld_arr_result, theme="streamlit", use_container_width=False)



##
## Countmer count analytics 
##
    
# Check if 'Total_Sales' column exists, and drop it if it does
# if 'Total_Sales' in replan_logo_metrics_df.columns:
#     replan_logo_metrics_df = replan_logo_metrics_df.drop(columns=['Total_Sales'])

st.subheader('Customer Counts')
cust_cout_tab1, cust_cout_tab2= st.tabs(["Final Customer Count", "Uploaded Coustomer Count"])

with cust_cout_tab1: 

    st.markdown("<br>", unsafe_allow_html=True)

    # customer count 
    replan_cust_count_result = ac.cust_count_chart(replan_logo_metrics_df, '#88b988', 'Adjusted Customer Count' )
    st.altair_chart(replan_cust_count_result, theme="streamlit", use_container_width=False)

    # customer count waterfall
    replan_cust_count_wf_result = ac.cust_count_waterfall_chart (replan_logo_metrics_df, 'Adjusted Customer Count Waterfall' )
    st.altair_chart(replan_cust_count_wf_result, theme="streamlit", use_container_width=False)


with cust_cout_tab2: 

    st.markdown("<br>", unsafe_allow_html=True)

    # customer count 
    replan_cust_count_result = ac.cust_count_chart(logo_metrics_df, '#77aaca', 'Uploaded Customer Count' )
    st.altair_chart(replan_cust_count_result, theme="streamlit", use_container_width=False)


    # Customer count waterfall 
    cust_count_wf_result = ac.cust_count_waterfall_chart (logo_metrics_df, 'Customer Count Waterfall' )
    st.altair_chart(cust_count_wf_result, theme="streamlit", use_container_width=False)



##
## Top customer analysis 
##
    
# Check if 'Total_Sales' column exists, and drop it if it does

st.subheader('Top Customers')
top_cust_tab1, top_cust_tab2= st.tabs(["Adjusted Values", "Uploaded Values"])


with top_cust_tab1:
    st.markdown("<br>", unsafe_allow_html=True)

    top_final_chart = ac.top_cust_chart(replan_customer_arr_df, '#99c999', 'Top Customers - Adjusted' )
    st.altair_chart(top_final_chart, theme="streamlit", use_container_width=False)

with top_cust_tab2:
    st.markdown("<br>", unsafe_allow_html=True)

    top_final_chart1 = ac.top_cust_chart(customer_arr_df, '#77aaca', 'Top Customers - Uploaded' )
    st.altair_chart(top_final_chart1, theme="streamlit", use_container_width=False)


##
## Customer MRR Analysis 
##  
st.subheader('Customer MRR Analysis')
cust_arr_tab1, cust_arr_tab2= st.tabs(["Adjusted Values", "Uploaded Values"])

with cust_arr_tab1: 

    st.markdown("<br>", unsafe_allow_html=True)

    df_original = replan_customer_arr_waterfall_df.copy()

    df = replan_customer_arr_waterfall_df[replan_customer_arr_waterfall_df['measureType'] == 'monthlyRevenue']

    # Create a unique identifier for each customer
    df['uniqueName'] = df['customerName'] + ' (' + df['customerId'].astype(str) + ')'

    # Dropdown to select customer by unique identifier
    selected_unique_name = st.selectbox("Select a Customer", df['uniqueName'].unique(), key="unique_customer_select-1")

    # Query the DataFrame to get customerId for the selected uniqueName
    selected_id = df[df['uniqueName'] == selected_unique_name]['customerId'].iloc[0]

    # Filter the dataframe based on customerId
    filtered_df = df_original[df_original['customerId'] == selected_id]

    st.markdown("<br>", unsafe_allow_html=True)
    mrr_wf_result = ac.cust_arr_waterfall_chart(filtered_df, 'Customer MRR Waterfall - Adjusted')

    st.altair_chart(mrr_wf_result, theme="streamlit", use_container_width=False)



with cust_arr_tab2: 

    st.markdown("<br>", unsafe_allow_html=True)

    df_original = customer_arr_waterfall_df.copy()

    df = customer_arr_waterfall_df[replan_customer_arr_waterfall_df['measureType'] == 'monthlyRevenue']

    # Create a unique identifier for each customer
    df['uniqueName'] = df['customerName'] + ' (' + df['customerId'].astype(str) + ')'

    # Dropdown to select customer by unique identifier
    selected_unique_name = st.selectbox("Select a Customer", df['uniqueName'].unique(), key="unique_customer_select-2")

    # Query the DataFrame to get customerId for the selected uniqueName
    selected_id = df[df['uniqueName'] == selected_unique_name]['customerId'].iloc[0]

    # Filter the dataframe based on customerId
    filtered_df = df_original[df_original['customerId'] == selected_id]

    st.markdown("<br>", unsafe_allow_html=True)
    mrr_wf_result = ac.cust_arr_waterfall_chart(filtered_df, 'Customer MRR Waterfall - Adjusted')

    st.altair_chart(mrr_wf_result, theme="streamlit", use_container_width=False)

