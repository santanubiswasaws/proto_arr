import streamlit as st
import pandas as pd
import altair as alt
from pandas.tseries.offsets import MonthEnd
from datetime import datetime, timedelta


from arr_lib.styling import BUTTON_STYLE
from arr_lib.styling import MARKDOWN_STYLES
from arr_lib.styling import GLOBAL_STYLING


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
with card_tab1:
    st.markdown("<br>", unsafe_allow_html=True)

    ##
    ## Prep data for metrics card
    ##

    # arr metrics 
    rp_df = replan_metrics_df.copy()

    # Melting the DataFrame
    rp_df = rp_df.melt(id_vars='measureType', var_name='month', value_name='value')

    # Sorting the unique months
    month_columns = sorted(rp_df['month'].unique(), reverse=True)

    # Calculate last month based on today's date
    today = datetime.today()
    first_day_of_this_month = today.replace(day=1)
    last_month_end = first_day_of_this_month - timedelta(days=1)
    last_month = last_month_end.strftime("%Y-%m")

    # Check if last_month is in the list of months, otherwise use the last available month
    default_month = last_month if last_month in month_columns else month_columns[-1]

    # Set selected_month to default_month initially
    selected_month = default_month

    # Dropdown to select the month with default set to last_month
    selected_month = st.selectbox("Select a Month", month_columns, index=month_columns.index(selected_month), key="arr_month_select_1" )
    filtered_data = rp_df[rp_df['month'] == selected_month].fillna(0) 


    # customer count metrics 
    rp_logo_df = replan_logo_metrics_df.copy()  
    rp_logo_df = rp_logo_df.melt(id_vars='measureType', var_name='month', value_name='value')
    rp_logo_df['month'] = pd.to_datetime(rp_logo_df['month']) + MonthEnd(0)


    # Filter for 'monthlyRevenueLogo'
    rp_cust_count = rp_logo_df[rp_logo_df['measureType'] == 'newBusinessLogo']

    # Get the current date to calculate the last 12 and 24 months
    selected_month_date = pd.to_datetime(selected_month) + MonthEnd(0)

    sum_last_12_months = rp_cust_count[(rp_cust_count['month'] <= selected_month_date) & 
                                    (rp_cust_count['month'] > selected_month_date - pd.DateOffset(months=12))]['value'].sum()

    sum_last_24_months = rp_cust_count[(rp_cust_count['month'] <= selected_month_date) & 
                                    (rp_cust_count['month'] > selected_month_date - pd.DateOffset(months=24))]['value'].sum()


    #
    # Print the metrics cards 
    #
    st.markdown("<br>", unsafe_allow_html=True)

    card_col1, card_col2, card_col3, card_col4 = st.columns(4)
    with card_col1: 

        # ARR and growth

        rp_arr = filtered_data.loc[(filtered_data['month'] == selected_month) & (filtered_data['measureType'] == 'monthlyRevenue'), 'value'].values[0] 
        rp_arr= rp_arr / 1000 
        rp_arr = "{:,.0f}".format(rp_arr)

        rp_arr_growth = filtered_data.loc[(filtered_data['month'] == selected_month) & (filtered_data['measureType'] == 'yearlyRevenueGrowth'), 'value'].values[0] 
        rp_arr_growth = "{:,.2f}%".format(rp_arr_growth)

        st.metric(label="ARR (in thousands)", value=rp_arr, delta=rp_arr_growth)


    with card_col2: 

        # New Logo 
        rp_logo_growth = ( sum_last_12_months / (sum_last_24_months - sum_last_12_months) ) * 100
        rp_logo_cnt = "{:,.0f}".format(sum_last_12_months)
        rp_logo_growth = "{:,.2f}%".format(rp_logo_growth)
        st.metric(label="New Logo in last 12 months", value=rp_logo_cnt, delta=rp_logo_growth)


    with card_col3: 

        # Net retention 
        rp_nr = filtered_data.loc[(filtered_data['month'] == selected_month) & (filtered_data['measureType'] == 'netRetentionRate'), 'value'].values[0] 
        if not rp_nr:
            rp_nr = 0
        rp_nr *= 100 
        rp_nr = "{:,.2f}%".format(rp_nr)
        st.metric(label="Net Retention (NRR))", value=rp_nr, delta=None)

    with card_col4: 

        # Gross retention 
        rp_gr = filtered_data.loc[(filtered_data['month'] == selected_month) & (filtered_data['measureType'] == 'grossRetentionRate'), 'value'].values[0] 
        rp_gr *= 100
        rp_gr = "{:,.2f}%".format(rp_gr)
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

    # Sorting the unique months
    met_month_columns = sorted(met_df['month'].unique(), reverse=True)

    # Calculate last month based on today's date
    today = datetime.today()
    first_day_of_this_month = today.replace(day=1)
    last_month_end = first_day_of_this_month - timedelta(days=1)
    last_month = last_month_end.strftime("%Y-%m")

    # Check if last_month is in the list of months, otherwise use the last available month
    default_month = last_month if last_month in month_columns else month_columns[-1]

    # Set selected_month to default_month initially
    met_selected_month = default_month

    # Dropdown to select the month with default set to last_month
    met_selected_month = st.selectbox("Select a Month",  met_month_columns, index=met_month_columns.index(met_selected_month), key="arr_month_select_2", )
    met_filtered_data = met_df[met_df['month'] == met_selected_month].fillna(0) 


    # customer count metrics 
    logo_df = logo_metrics_df.copy()  
    logo_df = logo_df.melt(id_vars='measureType', var_name='month', value_name='value')
    logo_df['month'] = pd.to_datetime(logo_df['month']) + MonthEnd(0)


    # Filter for 'monthlyRevenueLogo'
    cust_count = logo_df[logo_df['measureType'] == 'newBusinessLogo']

    # Get the current date to calculate the last 12 and 24 months
    met_selected_month_date = pd.to_datetime(met_selected_month) + MonthEnd(0)

    met_sum_last_12_months = cust_count[(cust_count['month'] <= met_selected_month_date) & 
                                    (cust_count['month'] > met_selected_month_date - pd.DateOffset(months=12))]['value'].sum()

    met_sum_last_24_months = cust_count[(cust_count['month'] <= met_selected_month_date) & 
                                    (cust_count['month'] > met_selected_month_date - pd.DateOffset(months=24))]['value'].sum()
    

    st.markdown("<br>", unsafe_allow_html=True)

    card_col1a, card_col2a, card_col3a, card_col4a = st.columns(4)
    with card_col1a: 

        # ARR and growth

        arr = met_filtered_data.loc[(met_filtered_data['month'] == met_selected_month) & (met_filtered_data['measureType'] == 'monthlyRevenue'), 'value'].values[0] 
        arr= arr / 1000 
        arr = "{:,.0f}".format(arr)

        arr_growth = met_filtered_data.loc[(met_filtered_data['month'] == met_selected_month) & (met_filtered_data['measureType'] == 'yearlyRevenueGrowth'), 'value'].values[0] 
        arr_growth = "{:,.2f}%".format(arr_growth)

        st.metric(label="ARR (in thousands)", value=arr, delta=arr_growth)



    with card_col2a: 

        # New Logo 
        logo_growth = ( met_sum_last_12_months / (met_sum_last_24_months - met_sum_last_12_months) ) * 100
        logo_cnt = "{:,.0f}".format(met_sum_last_12_months)
        logo_growth = "{:,.2f}%".format(logo_growth)
        st.metric(label="New Logo in last 12 months", value=logo_cnt, delta=logo_growth)

    with card_col3a: 

        # Net retention 
        nr = met_filtered_data.loc[(met_filtered_data['month'] == met_selected_month) & (met_filtered_data['measureType'] == 'netRetentionRate'), 'value'].values[0] 
        nr *= 100 
        nr = "{:,.2f}%".format(nr)
        st.metric(label="Net Retention (NRR))", value=nr, delta=None)

    with card_col4a: 

        # Gross retention 
        gr = met_filtered_data.loc[(met_filtered_data['month'] == met_selected_month) & (met_filtered_data['measureType'] == 'grossRetentionRate'), 'value'].values[0] 
        gr *= 100 
        gr = "{:,.2f}%".format(gr)
        st.metric(label="Gross Retention (NRR))", value=gr, delta=None)


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

