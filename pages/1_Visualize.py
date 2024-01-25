import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
import pandas as pd
import altair as alt
from pandas.tseries.offsets import MonthEnd
from datetime import datetime, timedelta


from arr_lib.styling import BUTTON_STYLE
from arr_lib.styling import MARKDOWN_STYLES
from arr_lib.styling import GLOBAL_STYLING

import arr_lib.arr_visualize as av
import arr_lib.arr_charts as ac

#st.image('insight_logo.png', use_column_width=False)
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
## Metrics card for last year 
## 1. ARR Growth, 2. New Customers, 3. NRR, 4. GRR
##

st.subheader('Core Metrics')

card_tab1, card_tab2= st.tabs(["Adjusted ARR", "Uploaded ARR"])

with card_tab1:  # Adjusted metrics 
    st.markdown("<br>", unsafe_allow_html=True)

    ##
    ## Prep data for metrics card
    ##

    # arr metrics 
    rp_df = replan_metrics_df.copy()
    rp_logo_df = replan_logo_metrics_df.copy()

    month_columns, default_month = av.get_list_of_months(rp_df, True)

    # Set selected_month to default_month initially
    selected_month = default_month

    # Dropdown to select the month with default set to last_month
    selected_month = st.selectbox("Select a Month", month_columns, index=month_columns.index(selected_month), key="arr_month_select_1" )
      
    rp_arr, rp_arr_growth, rp_logo_cnt, rp_logo_growth, rp_logo_churn, rp_logo_churn_rate, rp_nr, rp_gr = av.get_core_arr_metrics(rp_df, rp_logo_df, selected_month)
    
    #
    # Print the metrics cards 
    #
    st.markdown("<br>", unsafe_allow_html=True)

    card_col1, card_col2, card_col3, card_col4, card_col5 = st.columns(5)

    with card_col1: 
        # ARR and growth
        st.metric(label="ARR (in thousands)", value=rp_arr, delta=rp_arr_growth)

    with card_col2: 
        # New Logo 
        st.metric(label="New Logo in last 12 months", value=rp_logo_cnt, delta=rp_logo_growth)

    with card_col3: 
        # Churn
        st.metric(label="Churned Logo in last 12 months", value=rp_logo_churn, delta=rp_logo_churn_rate, delta_color="inverse")

    with card_col4: 
        # Net retention
        st.metric(label="Net Retention (NRR))", value=rp_nr, delta=None)

    with card_col5: 
        # Gross retention 
        st.metric(label="Gross Retention (GRR))", value=rp_gr, delta=None)


with card_tab2:

    st.markdown("<br>", unsafe_allow_html=True)

    ##
    ## Prep data for metrics card
    ##

    # arr metrics 
    met_df = metrics_df.copy()

    # Melting the DataFrame
    met_df = met_df.melt(id_vars='measureType', var_name='month', value_name='value')


        # arr metrics 
    met_df = metrics_df.copy()
    logo_df = logo_metrics_df.copy()

    month_columns_2, default_month_2 = av.get_list_of_months(met_df, True)

    # Set selected_month to default_month initially
    selected_month_2 = default_month_2

    # Dropdown to select the month with default set to last_month
    selected_month_2 = st.selectbox("Select a Month", month_columns_2, index=month_columns.index(selected_month_2), key="arr_month_select_2" )
      
    arr, arr_growth, logo_cnt, logo_growth, logo_churn, logo_churn_rate, nr, gr = av.get_core_arr_metrics(met_df, logo_df, selected_month_2)
    
    st.markdown("<br>", unsafe_allow_html=True)

    card_col1a, card_col2a, card_col3a, card_col4a, card_col5a = st.columns(5)

    with card_col1a: 
        # ARR and growth
        st.metric(label="ARR (in thousands)", value=arr, delta=arr_growth)

    with card_col2a: 
        # New Logo 
        st.metric(label="New Logo in last 12 months", value=logo_cnt, delta=logo_growth)

    with card_col3a: 
        st.metric(label="Churned Logo in last 12 months)", value=logo_churn, delta=logo_churn_rate, delta_color="inverse")

    with card_col4a: 
        st.metric(label="Net Retention (NRR))", value=nr, delta=None)

    with card_col5a: 
        # Gross retention 
        st.metric(label="Gross Retention (NRR))", value=gr, delta=None)


# Metrics card styling elements 
        
    # background_color: str = "#FFF",
    # border_size_px: int = 1,
    # border_color: str = "#CCC",
    # border_radius_px: int = 5,
    # border_left_color: str = "#9AD8E1",
    # box_shadow: bool = True,

style_metric_cards(
        border_color = "#CCC",
        border_left_color = "#E0E0E0",    
        box_shadow = False)


    # background_color: str = "#FFF",
    # border_size_px: int = 1,
    # border_color: str = "#CCC",
    # border_radius_px: int = 5,
    # border_left_color: str = "#9AD8E1",
    # box_shadow: bool = True,


st.markdown("<br><br>", unsafe_allow_html=True)
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

st.markdown(BUTTON_STYLE, unsafe_allow_html=True)
st.markdown(MARKDOWN_STYLES, unsafe_allow_html=True)
st.markdown(GLOBAL_STYLING, unsafe_allow_html=True)






