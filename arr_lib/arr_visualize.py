import streamlit as st
import pandas as pd
import altair as alt
from pandas.tseries.offsets import MonthEnd
from datetime import datetime, timedelta


def get_list_of_months(df, descending):
    """
    Given a dataframe with a column name called months - returns distinct months 
    """
    inpput_df = df.copy()

    # Melting the DataFrame
    inpput_df = inpput_df.melt(id_vars='measureType', var_name='month', value_name='value')

    # Sorting the unique months
    month_columns = sorted(inpput_df['month'].unique(), reverse = descending)

    # Calculate last month based on today's date
    today = datetime.today()
    first_day_of_this_month = today.replace(day=1)
    last_month_end = first_day_of_this_month - timedelta(days=1)
    last_month = last_month_end.strftime("%Y-%m")

    # Check if last_month is in the list of months, otherwise use the last available month
    last_month = last_month if last_month in month_columns else month_columns[-1]

    return month_columns,last_month

def get_core_arr_metrics (df_agg, df_logo, selected_month): 
    """
    Calculate the following metrics 

    1. ARR and growth over last 12 monhts 
    2. New Logo and growith over last 12 months 
    3. Churned Logo and rate of change over last 12 months 
    4. Net Retention Rate 
    5. Gross Retention Rate 

    @todo -  make the display structure dynamic - so that just by adding new metrics to the structure - it can be rendered automatically 
    """


    input_df_agg = df_agg.copy()
    input_df_agg = input_df_agg.melt(id_vars='measureType', var_name='month', value_name='value')
    filtered_data = input_df_agg[input_df_agg['month'] == selected_month].fillna(0) 

    # Get the current date to calculate the last 12 and 24 months
    selected_month_date = pd.to_datetime(selected_month) + MonthEnd(0)

    inpput_df_logo = df_logo.copy()
    logo_df = inpput_df_logo.melt(id_vars='measureType', var_name='month', value_name='value')
    logo_df['month'] = pd.to_datetime(logo_df['month']) + MonthEnd(0)

    # ARR metrics 
    arr = filtered_data.loc[(filtered_data['month'] == selected_month) & (filtered_data['measureType'] == 'monthlyRevenue'), 'value'].values[0] 
    arr= arr / 1000 
    arr = "{:,.0f}".format(arr)

    arr_growth = filtered_data.loc[(filtered_data['month'] == selected_month) & (filtered_data['measureType'] == 'yearlyRevenueGrowth'), 'value'].values[0] 
    arr_growth *= 100
    arr_growth = "{:,.2f}%".format(arr_growth)

    # Customer Count Metrics    
    # Filter for 'monthlyBusinessLogo'
    cust_count = logo_df[logo_df['measureType'] == 'newBusinessLogo']

    sum_last_12_months = cust_count[(cust_count['month'] <= selected_month_date) & 
                                    (cust_count['month'] > selected_month_date - pd.DateOffset(months=12))]['value'].sum()

    sum_last_24_months = cust_count[(cust_count['month'] <= selected_month_date) & 
                                    (cust_count['month'] > selected_month_date - pd.DateOffset(months=24))]['value'].sum()

    logo_growth = ( sum_last_12_months * 100 / (sum_last_24_months - sum_last_12_months) ) 
    logo_cnt = "{:,.0f}".format(sum_last_12_months)
    logo_growth = "{:,.2f}%".format(logo_growth)



    # Churn customer Metrics 
    # Filter for 'churnLogo'
    churn_count = logo_df[logo_df['measureType'] == 'churnLogo']

    # Get the current date to calculate the last 12 and 24 months

    churn_last_12_months = churn_count[(churn_count['month'] <= selected_month_date) & 
                                    (churn_count['month'] > selected_month_date - pd.DateOffset(months=12))]['value'].sum()

    churn_last_24_months = churn_count[(churn_count['month'] <= selected_month_date) & 
                                    (churn_count['month'] > selected_month_date - pd.DateOffset(months=24))]['value'].sum()

    churn_growth = ( churn_last_12_months * 100 / (churn_last_24_months - churn_last_12_months) ) 
    churn_cnt = "{:,.0f}".format(churn_last_12_months)
    churn_growth = "{:,.2f}%".format(churn_growth)


    # Net retention 
    nr = filtered_data.loc[(filtered_data['month'] == selected_month) & (filtered_data['measureType'] == 'netRetentionRate'), 'value'].values[0] 
    if not nr:
        nr = 0
    nr *= 100 
    nr = "{:,.2f}%".format(nr)

    # Gross retention 
    gr = filtered_data.loc[(filtered_data['month'] == selected_month) & (filtered_data['measureType'] == 'grossRetentionRate'), 'value'].values[0] 
    gr *= 100
    gr = "{:,.2f}%".format(gr)

    return arr, arr_growth, logo_cnt, logo_growth, churn_cnt, churn_growth, nr, gr 
 