import pandas as pd
from datetime import datetime
import streamlit as st
from arr_lib.setup import ARR_DISPLAY_COLUMN_MAP
from arr_lib.styling import DF_HIGHLIGHT_TEXT_COLOR, DF_HIGHLIGHT_TEXT_WEIGHT
from arr_lib.styling import DF_NEGATIVE_HIGHLIGHT_BG_COLOR, DF_POSITIVE_HIGHLIGHT_BG_COLOR
from arr_lib.styling import DF_HIGHLIGHT_BG_COLOR_CURR_PERIOD, DF_HIGHLIGHT_BG_COLOR_PREV_PERIOD

# implemented with presetting the number of months

@st.cache_data
def create_monthly_buckets(df):
    """
        Process uploaded contract data 
        1. Validates all the columns 
        2. Breaks the uploaded records into monthly value - based on the contract lenght - create one row per month 
        3. Assigns the monthly monthlyRevenue amount for each month 

    Parameters:
    - df (pd.DataFrame): Original contract data DataFrame.

    Returns:
    - pd.DataFrame: Processed DataFrame one row for each month - for the customer and contract 
    """

    # Calculate contractMonths by rounding contractLength/30 - added 0.01 for boundary conditions
    df['contractMonths'] = ((df['contractDuration'] / 30) + 0.01).round()


    # handle missing contactId situations - defaults it to customerId + index of the row (unique)
    df['contractId'].fillna(df['customerId'].astype(str) + df.index.astype(str), inplace=True)

    # handle repeating contractId situation - concatenate contractId with index
    df['contractId'] = df['contractId'].astype(str) + df.index.astype(str)

    # Repeat rows based on contractMonths
    second_df = df.loc[df.index.repeat(df['contractMonths'].astype(int))].reset_index(drop=True)

    # handle missing contactId situations - defaults it to customerId + index of the row (unique)
    # second_df['contractId'].fillna(second_df['customerId'].astype(str) + second_df.index.astype(str), inplace=True)

    # Add a column called monthIndex and increment it by 1 for each customerId and contractId
    second_df['monthIndex'] = second_df.groupby(['customerId', 'contractId']).cumcount() + 1

    # Convert monthIndex to integers and calculate the 'month' column
    second_df['monthIndex'] = second_df['monthIndex'].astype(int)

    # increments the month fields based on monthIndex
    second_df['month'] = second_df.apply(lambda row: row['contractStartDate'] + pd.DateOffset(months=row['monthIndex'] - 1), axis=1)

    # Reformat 'month' to YYYY-MM format (drop the day portion)
    second_df['month'] = second_df['month'].dt.strftime('%Y-%m')

    # Add a column called monthlyRevenue
    second_df['monthlyRevenue'] = second_df['totalContractValue'] / second_df['contractMonths']

    # Fill NaN values with 0 for 'monthlyRevenue'
    second_df['monthlyRevenue'] = second_df['monthlyRevenue'].round(2).fillna(0)


    # filter only the following columns - customerId, contractId, month, monthlyRevenue 
    second_df = second_df[['customerId', 'customerName', 'contractId', 'month', 'monthlyRevenue']]

    return second_df


@st.cache_data
def create_arr_metrics(df):
    """
    Process df containing monthly rr values for each customer and generates aggregated value.
    Also create the wwaterfall or flow of ARR 

    Parameters:
    - df (pd.DataFrame): Dataframe with each row containing customer and month level contract value - monthlyRevenue

    Returns: 2 data frames
    - pd.DataFrame: Dataframe with transposed data for each customer - for each month becoming a column, also gives customer level aggregated revenue
    - pd.DataFrame: Gives the over all metrics for each month, agrregatd for all customers - MRR, ARR, newBusiness, upSell, downSell, churn 
    """

    transposed_df = create_transposed_monthly_revenue_matrix(df)
    customer_arr_df, logo_waterfall_df, metrics_df = create_customer_and_aggregated_metrics(transposed_df)

    return customer_arr_df, logo_waterfall_df, metrics_df


@st.cache_data
def create_transposed_monthly_revenue_matrix (df): 
    """
    Process df containing monthly rr values for each customer and creates a transposed dataframe

    Parameters:
    - df (pd.DataFrame): Dataframe with each row containing customer and month level contract value

    Returns:
    - pd.DataFrame: Dataframe with transposed data - for each month becoming a column, also gives customer level aggregated revenue
    """


    # Print the original dataframe
    print("Original DataFrame:")

    # select only the required columns 
    df = df.loc[:, ['customerName', 'customerId', 'month', 'monthlyRevenue']]


    # Transpose the melted dataframe
    transposed_df = df.pivot_table(index=['customerName', 'customerId'],
                                        columns='month', values='monthlyRevenue', fill_value=0, aggfunc='sum').reset_index()
    
    # Remove the month as index 
    transposed_df.columns.name = None  # Remove the 'month' label


    return transposed_df


@st.cache_data
def create_customer_and_aggregated_metrics(df):
    """
    Process df containing transposed monthly metrics for each customer with aggregated monthly revenue, and calculates the following metrics
        newBusiness 
        upSell
        downSell
        churn 

    Parameters:
    - df (pd.DataFrame): transposed monthly metrics for each customer with aggregated monthly revenue

    Returns:
    - pd.DataFrame: Gives the over all metrics for each month for each customer - MRR, ARR, newBusiness, upSell, downSell, churn 
    - pd.DataFrame: Gives the over all logo count waterfall 
    - pd.DataFrame: Gives aggregated metrics  - MRR, ARR, newBusiness, upSell, downSell, churn 
    """


    df.insert(2, 'measureType', 'monthlyRevenue')

    # Identify 'newBusiness' rows based on the condition
    new_business_mask = (df.shift(axis=1, fill_value=0) == 0) & (df != 0)

    # Create a new DataFrame with 'newBusiness' rows
    new_business_df = df[new_business_mask].copy()
    new_business_df['measureType'] = 'newBusiness'

    # Fill NaN values with 0
    new_business_df = new_business_df.fillna(0)

    # Retrieve the 'customerId' values for 'upSell' rows
    new_business_df['customerId'] = df.loc[new_business_mask.index, 'customerId'].values
    # Retrieve the 'customerName' values for 'upSell' rows
    new_business_df['customerName'] = df.loc[new_business_mask.index, 'customerName'].values



    # Identify 'upSell' rows based on the condition for all month columns
    df_numeric = df.iloc[:, 2:].apply(pd.to_numeric, errors='coerce')  # Convert columns to numeric
    up_sell_mask = (df_numeric.diff(axis=1) > 0) & (df_numeric.shift(axis=1) != 0)
    up_sell_df = (df_numeric[up_sell_mask] - df_numeric.shift(axis=1))[up_sell_mask].copy()
    up_sell_df['measureType'] = 'upSell'

    # Mask to make 'upSell' rows zero when the previous month's 'monthlyRevenue' is 0 for all month columns
    zero_month_mask = (df_numeric.iloc[:, :-1] == 0)
    up_sell_df[zero_month_mask] = 0

    # Retrieve the 'customerId' values for 'upSell' rows
    up_sell_df['customerId'] = df.loc[up_sell_mask.index, 'customerId'].values
    # Retrieve the 'customerName' values for 'upSell' rows
    up_sell_df['customerName'] = df.loc[up_sell_mask.index, 'customerName'].values

    # Identify 'downSell' rows based on the condition for all month columns
    down_sell_mask = (df_numeric.diff(axis=1) < 0) & (df_numeric.shift(axis=1) != 0) & (df_numeric !=0 )
    down_sell_df = (df_numeric[down_sell_mask] - df_numeric.shift(axis=1))[down_sell_mask].copy()
    down_sell_df['measureType'] = 'downSell'

    # Retrieve the 'customerId' values for 'downSell' rows
    down_sell_df['customerId'] = df.loc[down_sell_mask.index, 'customerId'].values
    # Retrieve the 'customerName' values for 'downSell' rows
    down_sell_df['customerName'] = df.loc[down_sell_mask.index, 'customerName'].values

    # Calculate 'churn' rows based on the specified condition
    churn_mask = (df_numeric.diff(axis=1) < 0) & (df_numeric == 0)
    churn_df = (df_numeric[churn_mask] - df_numeric.shift(axis=1))[churn_mask].copy()
    churn_df['measureType'] = 'churn'


    # Retrieve the 'customerId' values for 'churn' rows
    churn_df['customerId'] = df.loc[churn_mask.index, 'customerId'].values
    # Retrieve the 'customerName' values for 'churn' rows
    churn_df['customerName'] = df.loc[churn_mask.index, 'customerName'].values


    # Append 'upSell', 'downSell', and 'churn' rows to the original DataFrame
    df = pd.concat([df, up_sell_df, down_sell_df, churn_df], ignore_index=True)

    # Append 'newBusiness' rows to the original DataFrame
    df = pd.concat([df, new_business_df], ignore_index=True)

    # Fill NaN values with 0
    df = df.fillna(0)

    # Define the sorting order for 'measureType'
    sorting_order = ['monthlyRevenue', 'newBusiness', 'upSell', 'downSell', 'churn']

    # Sort the DataFrame based on 'measureType' using the defined order and 'customerId'
    df['measureType'] = pd.Categorical(df['measureType'], categories=sorting_order, ordered=True)
    df = df.sort_values(['customerName','customerId', 'measureType'])

    # select only the monthlyRevenue for csutomer level details 
    df_rr = df[df['measureType'] == 'monthlyRevenue']

    # remove the measureType column from customer level arr details 
    del df_rr['measureType']

    # sort mothly_revenue matrix, but first month of sales
    df_rr = sort_by_first_month_of_sales(df_rr)

    # create aggregated metrics from customer level metrics 
    df_agg = create_aggregated_arr_metrics(df)

    # convert the aggregated df to a waterfall structure
    df_agg = create_waterfall(df_agg)
    
    # multiply monthly numbers by 12 to annualize 
    df_agg = annualize_agg_arr(df_agg)

    # create additional metrics - like gross renewal rate, net renewal rate etc
    df_agg = calculate_retention_metrics(df_agg)

    # create logo waterfall 
    df_logo_waterfall = calculate_logo_count_waterfall(df)

    # print(df_logo_waterfall)

    return df_rr, df_logo_waterfall, df_agg


@st.cache_data
def create_aggregated_arr_metrics(df):
    """
    Process df containing transposed monthly metrics for each customer, aggregates the values for all customers and returns the aggregated df

    Parameters:
    - df (pd.DataFrame): transposed monthly metrics for each customerlevel with revenue, new buessiness, upsell, downsell and churn

    Returns:
    - pd.DataFrame: Gives the over all metrics for each month - MRR, ARR, newBusiness, upSell, downSell, churn 
    """


    # Group by 'customerId', 'CustomerName' and aggregate the sum across all measureTypes for each month
    aggregated_df = df.groupby(['measureType'], observed=True).agg({col: 'sum' for col in df.columns[3:]}).reset_index()

    return aggregated_df

@st.cache_data
def calculate_retention_metrics (df):
    """
    calculates the following metrics 
        - Gross Renewal Rate : measured as 1 - { (cummulative sum of last 12 months churn and downsell ) / revenue of 12 month prior } 
        - Net Retention Rate : measured as 1 - { (cummulative sum of last 12 months upsell, churn and downsell ) / revenue of 12 month prior  } 
        - Yearly ARR Growth: measured as   ( current period reenue / revenue of 12 month prior) - 1
    """

    upSell_df = df[df['measureType']=='upSell']
    downSell_df = df[df['measureType']=='downSell']
    churn_df = df[df['measureType']=='churn']
    monthlyRev_df = df[df['measureType']=='monthlyRevenue']

    # caculate trailing yearly metrics 
    trailing_period = 12

    trailing_upSell_df = calculate_trailing_metrics(upSell_df, trailing_period, 'trailingUpSell')
    trailing_downSell_df = calculate_trailing_metrics(downSell_df, trailing_period, 'trailingDownSell')
    trailing_churn_df = calculate_trailing_metrics(churn_df, trailing_period, 'trailingChurn')
    previous_period_revenue = calculate_previous_period_values(monthlyRev_df, trailing_period, 'monthlyRevenue', 'prevYearRevenue')

  
    temp_metrics_df = pd.concat([df, trailing_upSell_df, trailing_downSell_df, trailing_churn_df, previous_period_revenue ], ignore_index=True)

    # transpose the df - so that measureType become columns and months become rows
    temp_metrics_df = temp_metrics_df.transpose()
    temp_metrics_df.columns = temp_metrics_df.iloc[0]  # Set the first row as column headers
    temp_metrics_df = temp_metrics_df[1:]  # Remove the first row

    temp_metrics_df['grossRenewalRate'] = temp_metrics_df.apply(lambda row: (1 + (row['trailingDownSell'] + row['trailingChurn']) / row['prevYearRevenue']) if row['prevYearRevenue'] is not None else None, axis=1)
    temp_metrics_df['netRetentionRate'] = temp_metrics_df.apply(lambda row: (1 + (row['trailingDownSell'] + row['trailingChurn'] + row['trailingUpSell']) / row['prevYearRevenue']) if row['prevYearRevenue'] is not None else None, axis=1)
    temp_metrics_df['yearlyRevenueGrowth'] = temp_metrics_df.apply(lambda row: ( row['monthlyRevenue']  / row['prevYearRevenue'] - 1) if row['prevYearRevenue'] is not None else None, axis=1)

    # transpose back 
    temp_metrics_df = temp_metrics_df.transpose()
    temp_metrics_df.reset_index(inplace=True)
    temp_metrics_df.rename(columns={'index': 'measureType'}, inplace=True)

    return temp_metrics_df

@st.cache_data
def calculate_trailing_metrics(df, trailing_period, newMeasureType): 
    """
    calculates the trailing cummulative sum of a metrics for a given period 
    """
    df = df.transpose()
    df.columns = df.iloc[0]  # Set the first row as column headers
    df = df[1:]  # Remove the first row

    # return rolling cummulative period 
    cum_column_df =  df.rolling(window=trailing_period, min_periods=1).sum()
    
    df[newMeasureType] = cum_column_df
    df_transposed = df.transpose()
    df_transposed.reset_index(inplace=True)
    df_transposed.rename(columns={'index': 'measureType'}, inplace=True)

    return df_transposed[df_transposed['measureType']==newMeasureType]


@st.cache_data
def calculate_previous_period_values(df, trailing_period, measureType, newMeasureType): 
    """
    calculates the trailing cummulative sum of a metrics for a given period 
    """
    df = df.transpose()
    df.columns = df.iloc[0]  # Set the first row as column headers
    df = df[1:]  # Remove the first row

    # return rolling cummulative period 
    prev_df =  df[measureType].shift(trailing_period)

    df[newMeasureType] = prev_df
    df_transposed = df.transpose()
    df_transposed.reset_index(inplace=True)
    df_transposed.rename(columns={'index': 'measureType'}, inplace=True)

    return  df_transposed[df_transposed['measureType']==newMeasureType]


@st.cache_data
def calculate_logo_count_waterfall (df):
    """
    calculates the logo waterfall metrics 
        Beging Customer Count
        New Customers Count
        Churn Customers Count
        Ending Customers Count 
    """


    # filter out upsell and downsell records 

    # categorical value are cached and gives erratic behavior 
    df['measureType'] = df['measureType'].astype(str)
    filtered_df = df[df['measureType'].isin(['monthlyRevenue', 'newBusiness', 'churn'])]

    # Melt the DataFrame to have a single 'value' column for months
    melted_df = pd.melt(filtered_df, id_vars=['customerId', 'customerName', 'measureType'], var_name='month', value_name='value')
    melted_df['value'].fillna(0, inplace=True)

    # Filter rows with non-zero values
    non_zero_df = melted_df[melted_df['value'] != 0]

    # Group by month, measureType, and count distinct customers
    result_df = non_zero_df.groupby(['month', 'measureType'])['customerId'].count().reset_index()

    # turn values in the 'churn' row to negative - the column where the ount is stored is customerId - because of group by 
    result_df.loc[result_df['measureType'] == 'churn', 'customerId'] *= -1

    # Pivot the result to have months as columns and measuretype as index
    final_df = result_df.pivot_table(index='measureType', columns='month', values='customerId', aggfunc='sum', fill_value=0)

    # Reset the index and remove the 'month' index name
    final_df.reset_index(inplace=True)
    final_df.columns.name = None

    # Change the values in the measureType columns to include a suffix  "Logo" without using a for loop
    final_df['measureType'] = final_df['measureType'].apply(lambda x: f'{x}Logo')

    # Copy the monthly revenue to waterfall final_df 
    logo_wf_df = final_df[final_df['measureType']=='monthlyRevenueLogo'].copy()

    # Shift the columns of the original final_df - by one colmn- and add it  to waterfall final_df - so that it now captures last month's revenue
    logo_wf_df.iloc[0, 2:] = logo_wf_df.iloc[0, 1:-1].values
    logo_wf_df['measureType'] = 'lastMonthRevenueLogo'


    # concat the lastMonthrevenue to the final_df
    logo_wf_df = pd.concat([logo_wf_df, final_df], ignore_index=True)

    # Define the sorting order for 'measureType'
    sorting_order = ['lastMonthRevenueLogo', 'newBusinessLogo',  'churnLogo', 'monthlyRevenueLogo']

    # Sort the DataFrame based on 'measureType' using the defined order and 'customerId'
    logo_wf_df['measureType'] = pd.Categorical(logo_wf_df['measureType'], categories=sorting_order, ordered=True)
    logo_wf_df = logo_wf_df.sort_values(['measureType'])


    return logo_wf_df


@st.cache_data
def create_waterfall(df): 
    """
    Process df containing monthly rr metrics, and add the previous months revenue as the opening balance and then reorders the rows as
        lastMonthRevenue 
        newBusiness
        upSell 
        downSell
        churn 
        currentMonthRevenue 

    Parameters:
    - df (pd.DataFrame): Dataframe with aggreagated month rr metrics 

    Returns:
    - pd.DataFrame: Dataframe with waterfall details 
    """

    # CCopy the monthly revenue to waterfall df 
    waterfall_df = df[df['measureType']=='monthlyRevenue'].copy()

    # Shift the columns of the original df - by one colmn- and add it  to waterfall df - so that it now captures last month's revenue
    waterfall_df.iloc[0, 2:] = df.iloc[0, 1:-1].values

    waterfall_df['measureType'] = waterfall_df['measureType'].cat.add_categories(['lastMonthRevenue'])

    # rename the row measureType 
    waterfall_df.iloc[0, 0] = "lastMonthRevenue"

    # concat the lastMonthrevenue to to the df
    waterfall_df = pd.concat([waterfall_df, df], ignore_index=True)

    # Define the sorting order for 'measureType'
    sorting_order = ['lastMonthRevenue', 'newBusiness', 'upSell', 'downSell', 'churn', 'monthlyRevenue']

    # Sort the DataFrame based on 'measureType' using the defined order and 'customerId'
    waterfall_df['measureType'] = pd.Categorical(waterfall_df['measureType'], categories=sorting_order, ordered=True)
    waterfall_df = waterfall_df.sort_values(['measureType'])

    return waterfall_df


@st.cache_data
def sort_by_first_month_of_sales(df): 
    """
    Sort the df containing monthwise customer revenue grid, in the order of first month of sale

    Parameters:
    - df (pd.DataFrame): Dataframe with monthwise customer revenue grid

    Returns:
    - pd.DataFrame: Same grid but sorted in first month of sales 
    """

    # assumes the first 2 columns are customerId, customerName

    # Create a new column 'first_non_zero_month' to store the name of the first non-zero sales month
    df['first_non_zero_month'] = (df.iloc[:, 2:] != 0).idxmax(axis=1)

    # Create a new column 'last_non_zero_month' to store the name of the last non-zero sales month
    df['last_non_zero_month'] = (df.iloc[:, 2:-1].apply(lambda x: x.iloc[::-1].ne(0).idxmax() if x.any() else 'NaN', axis=1))

    # 'first_non_zero_month', 'last_non_zero_month', and finally by 'customerId'
    sorted_df = df.sort_values(by=[ 'first_non_zero_month', 'last_non_zero_month', 'customerId'])

    # Reset the index if needed
    sorted_df.reset_index(drop=True, inplace=True)

    # Drop the 'first_non_zero_month' and 'last_non_zero_month' columns
    sorted_df.drop(columns=['first_non_zero_month', 'last_non_zero_month'], inplace=True)

    return sorted_df


@st.cache_data
def annualize_agg_arr(df): 
    """
    Converts MRR to ARR 

    Parameters:
    - df (pd.DataFrame): Dataframe with monthly waterfall MRR view

    Returns:
    - pd.DataFrame: Annualized waterfall df 
    """
    annualized_df = df

#    Select the numerical columns (excluding 'measureType')
    numerical_columns = annualized_df.columns.difference(['measureType'])

    # Multiply the numerical columns by 12
    annualized_df[numerical_columns] = annualized_df[numerical_columns] * 12

    return annualized_df


@st.cache_data
def rename_columns(df):
    """
    Converts the name of the ARR metrcis to meaningful display values

    Parameters:
    - df (pd.DataFrame): Dataframe with ARR metrics 

    Returns:
    - pd.DataFrame: Same dataframe but the values in the measureType column is transalted based on the ARR_DISPLAY_COLUMN_MAP dict
    """
    # Replace 'measureType' values based on the mapping dictionary
    df['measureType'] = df['measureType'].replace(ARR_DISPLAY_COLUMN_MAP)

    return df


def stylize_metrics_df(df):
    """
    Stylize the dataframe using pandas styler class and applymap 
    """

    # drop metrics with intermediate
    # transpose the df - so that measureType become columns and months become rows
    stylized_df = df.transpose()
    stylized_df.columns = stylized_df.iloc[0]  # Set the first row as column headers
    stylized_df = stylized_df[1:]  # Remove the first row

    # filter only the relevant columns
    stylized_df = stylized_df[['lastMonthRevenue', 'newBusiness', 'upSell', 'downSell', 'churn', 'monthlyRevenue', 'grossRenewalRate', 'netRetentionRate', 'yearlyRevenueGrowth']]

    # these metrics are formatted with 0 precision 
    stylized_df['lastMonthRevenue'] = stylized_df['lastMonthRevenue'].apply(lambda x: '{:,.0f}'.format(x) if not pd.isnull(x)  else None)
    stylized_df['newBusiness'] = stylized_df['newBusiness'].apply(lambda x: '{:,.0f}'.format(x) if not pd.isnull(x)  else None)
    stylized_df['upSell'] = stylized_df['upSell'].apply(lambda x: '{:,.0f}'.format(x) if not pd.isnull(x)  else None)
    stylized_df['downSell'] = stylized_df['downSell'].apply(lambda x: '{:,.0f}'.format(x) if not pd.isnull(x)  else None)
    stylized_df['churn'] = stylized_df['churn'].apply(lambda x: '{:,.0f}'.format(x) if not pd.isnull(x)  else None)
    stylized_df['monthlyRevenue'] = stylized_df['monthlyRevenue'].apply(lambda x: '{:,.0f}'.format(x) if not pd.isnull(x)  else None)

    # these metrics are formatted as % with 2 digit precision 
    stylized_df['grossRenewalRate'] = stylized_df['grossRenewalRate'].apply(lambda x: '{:,.2%}'.format(x) if not pd.isnull(x)  else None)
    stylized_df['netRetentionRate'] = stylized_df['netRetentionRate'].apply(lambda x: '{:,.2%}'.format(x) if not pd.isnull(x)  else None)
    stylized_df['yearlyRevenueGrowth'] = stylized_df['yearlyRevenueGrowth'].apply(lambda x: '{:,.2%}'.format(x) if not pd.isnull(x)  else None)

    # transpose back 
    stylized_df = stylized_df.transpose()
    stylized_df.reset_index(inplace=True)
    stylized_df.rename(columns={'index': 'measureType'}, inplace=True)

    # replace the metrics name to redable values as per map 
    stylized_df = rename_columns(stylized_df)

    stylized_df.set_index(['measureType'], inplace=True)

    stylized_df=decorate_agg_metrics(stylized_df)

    return stylized_df


@st.cache_data
def reconcile_overrides(original_df, override_df):
    """
    Compares the scratchpad and override dfs - and create a recon_df with the difference in values for a given customer and month

    Parameters:
    - original_df (pd.DataFrame): Original DataFrame
    - override_df (pd.DataFrame): Override DataFrame

    Returns:
    - pd.DataFrame: DataFrame with differences between the two input DataFrames, truncated to the columns of override_df
    """

    # Replace NaN values with zeros in both DataFrames
    original_df.fillna(0, inplace=True)
    override_df.fillna(0, inplace=True)

    # Melt the DataFrames to convert months into rows
    melted_df_original = pd.melt(original_df, id_vars=['customerId', 'customerName'], var_name='month', value_name='value_original')
    melted_df_override = pd.melt(override_df, id_vars=['customerId', 'customerName'], var_name='month', value_name='value_override')

    # Merge the melted DataFrames on 'customerId', 'customerName', and 'month'
    merged_df = melted_df_original.merge(melted_df_override, on=['customerId', 'customerName', 'month'], how='outer')

    # Calculate the differences for each row using vectorized operations
    merged_df['difference'] =  merged_df['value_override'].fillna(0) - merged_df['value_original'].fillna(0)

    # Create a new DataFrame containing 'customerId', 'customerName', 'month', and 'difference'
    result_df = merged_df[['customerId', 'customerName', 'month', 'difference']]

    # Sort the result DataFrame by 'customerId' and 'month'
    result_df.sort_values(by=['customerId', 'month'], inplace=True)

    # Transpose the result DataFrame to make months become columns
    transposed_result_df = result_df.pivot_table(index=['customerId', 'customerName'], columns='month', values='difference', fill_value=0).reset_index()

    # Remove the month as index
    transposed_result_df.columns.name = None  # Remove the 'month' label

    # Truncate the resulting DataFrame to the columns of override_df
    truncated_df = transposed_result_df[override_df.columns]

    # Drop rows where all columns except 'customerId' and 'customerName' have a value of 0
    truncated_df = truncated_df[(truncated_df.drop(['customerId', 'customerName'], axis=1) != 0).any(axis=1)]


    return truncated_df


def highlight_positive_negative_cells(df):
    """
    Apply Pandas dataframe styles - 
    """

    pos_bg = DF_POSITIVE_HIGHLIGHT_BG_COLOR
    neg_bg = DF_NEGATIVE_HIGHLIGHT_BG_COLOR
    text_color = DF_HIGHLIGHT_TEXT_COLOR
    text_weight = DF_HIGHLIGHT_TEXT_WEIGHT

    # Apply styling to the DataFrame, excluding 'customerId' and 'customerName' columns
    styled_df = df.style.applymap(lambda val: style_positive_negative_lambda(val, pos_bg, neg_bg, text_color, text_weight ))

    return styled_df



def style_positive_negative_lambda(val, positive_bg_color, negative_bg_color, text_color, text_weight ):
    """
    Takes a scalar and returns a string with the css property
    for red color if the value is negative, and green if it's greater than 0.
    """
    if val < 0:
        return f'background-color: {negative_bg_color}; color: {text_color}; font-weight: {text_weight}'
    elif val > 0:
        return f'background-color: {positive_bg_color}; color: {text_color}; font-weight: {text_weight}'
    else:
        return ''
    

@st.cache_data    
def insert_blank_row(df, row_index, index_value, fill_value): 
    """
    Insert a blank row into a DataFrame at the specified row index, 
    maintaining the categorical 'measureType' index.

    :param df: Original DataFrame.
    :param row_index: Index at which the blank row should be inserted.
    :return: New DataFrame with the blank row inserted.
    """
    # Create a DataFrame with a single blank row
    blank_row = pd.DataFrame({col: fill_value for col in df.columns}, index=[row_index])
    
    # Concatenate the original DataFrame with the blank row DataFrame
    df_updated = pd.concat([df.iloc[:row_index], blank_row, df.iloc[row_index:]])

    # Reassign 'measureType' index values
    measureType_values = df.index.get_level_values('measureType').tolist()
    measureType_values.insert(row_index, index_value)  # Insert a placeholder for the blank row
    df_updated.index = pd.Index(measureType_values, name='measureType')
    
    return df_updated


def decorate_agg_metrics(df):
    """
    Apply Pandas dataframe styles to the aggregated metrics df 
    currently the following decorations are implemented 

    1. insert a blank separator row 
    2. Highlight negatives values in color red 
    3. Highlight the opening anfd closing period ARR is shades of green 
    
    Note: Streamlit has does not render all the pandas styling 
    """

    # insert a blank row after aggregated ARR metrics 
    df = insert_blank_row(df, 6, '-------------------------------------------------', '--------')

    neg_bg = DF_NEGATIVE_HIGHLIGHT_BG_COLOR
    curr_period_bg = DF_HIGHLIGHT_BG_COLOR_CURR_PERIOD
    prev_period_bg = DF_HIGHLIGHT_BG_COLOR_PREV_PERIOD
    text_color = DF_HIGHLIGHT_TEXT_COLOR
    text_weight = DF_HIGHLIGHT_TEXT_WEIGHT

    # Function to apply styling to each cell
    def style_cell(val):
        # Check for None, empty string, spaces, or strings starting with '--'
        if val is None or val == '' or str(val).isspace() or str(val).startswith('--'):
            return ''
        try:
            val_num = float(str(val).replace(",", "").replace("%", ""))
            if val_num < 0:
                return f'color: {neg_bg}; font-weight: {text_weight}'
            else:
                return ''
        except ValueError:
            return ''

    # Function to apply styling to each row
    def style_row(row):
        if row.name == 'Opening Period ARR':
            return [f'background-color: {prev_period_bg}'] * len(row)
        elif row.name == 'Closing Period ARR':
            return [f'background-color: {curr_period_bg}'] * len(row)
        else:
            return [''] * len(row)

    # Apply styling to each cell
    styled_df = df.style.apply(lambda x: x.map(style_cell), axis=None)

    # Apply styling to each row
    styled_df = styled_df.apply(style_row, axis=1)

    # Set text alignment
    styled_df = styled_df.set_properties(**{'text-align': 'right'}) # does not work with current Streamlit version

    return styled_df


def decorate_logo_metrics_df(df):
    """
    Apply Pandas dataframe styles to the aggregated metrics df 
    currently the following decorations are implemented 

    1. Highlight negatives values in color red 
    2. Highlight the opening anfd closing period ARR is shades of green 
    
    Note: Streamlit has does not render all the pandas styling 
    """

    neg_bg = DF_NEGATIVE_HIGHLIGHT_BG_COLOR
    curr_period_bg = DF_HIGHLIGHT_BG_COLOR_CURR_PERIOD
    prev_period_bg = DF_HIGHLIGHT_BG_COLOR_PREV_PERIOD
    text_color = DF_HIGHLIGHT_TEXT_COLOR
    text_weight = DF_HIGHLIGHT_TEXT_WEIGHT

    # Function to apply styling to each cell
    def style_cell(val):
        # Check for None, empty string, spaces, or strings starting with '--'
        if val is None or val == '' or str(val).isspace() or str(val).startswith('--'):
            return ''
        try:
            val_num = float(str(val).replace(",", "").replace("%", ""))
            if val_num < 0:
                return f'color: {neg_bg}; font-weight: {text_weight}'
            else:
                return ''
        except ValueError:
            return ''

    # Function to apply styling to each row
    def style_row(row):
        if row.name == 'Opening Period Customers':
            return [f'background-color: {prev_period_bg}'] * len(row)
        elif row.name == 'Closing Period Customers':
            return [f'background-color: {curr_period_bg}'] * len(row)
        else:
            return [''] * len(row)

    # Apply styling to each cell
    styled_df = df.style.apply(lambda x: x.map(style_cell), axis=None)

    # Apply styling to each row
    styled_df = styled_df.apply(style_row, axis=1)

    # Set text alignment
    styled_df = styled_df.set_properties(**{'text-align': 'right'}) # does not work with current Streamlit version

    return styled_df


@st.cache_data
def apply_overrides(original_df, override_df ):
    """
    Compares the scratchpad and override dfs - and create a recon_df with the difference in values for a given customer and month

    Parameters:
    - scratch_pad_df (pd.DataFrame): scratch pad df 
    - override_df  (pd.DataFrame): override df 

    Returns:
    - pd.DataFrame: for each customer as row and months as columns, it creates the differnce between the tow input dfs 
    """


    # Melt the DataFrames to convert months into rows
    melted_df_original = pd.melt(original_df, id_vars=['customerId', 'customerName'], var_name='month', value_name='value_original')
    melted_df_override = pd.melt(override_df, id_vars=['customerId', 'customerName'], var_name='month', value_name='value_override')

    # Merge the melted DataFrames on 'customerId', 'customerName', and 'month'
    merged_df = melted_df_original.merge(melted_df_override, on=['customerId', 'customerName', 'month'], how='outer')

    # Apply the logic: if value_override is not NaN, use it, otherwise, use the value from value_edited
    merged_df['value'] = merged_df.apply(lambda row: row['value_override'] if not pd.isna(row['value_override']) else row['value_original'], axis=1)

    # Create a new DataFrame containing 'customerId', 'customerName', 'month', and 'difference'
    result_df = merged_df[['customerId', 'customerName', 'month', 'value']]

    # Sort the result DataFrame by 'customerId' and 'month'
    result_df.sort_values(by=['customerId', 'month'], inplace=True)

    # Transpose the result DataFrame to make months become columns
    transposed_result_df = result_df.pivot_table(index=['customerId', 'customerName'], columns='month', values='value', fill_value=0).reset_index()

    # Remove the month as index 
    transposed_result_df.columns.name = None 

    # sort the dataset by first month of sales 
    transposed_result_df = sort_by_first_month_of_sales(transposed_result_df)

    return transposed_result_df
