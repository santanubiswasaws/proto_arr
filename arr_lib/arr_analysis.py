import pandas as pd
from datetime import datetime
import streamlit as st
from arr_lib.setup import ARR_DISPLAY_COLUMN_MAP

# implemented with presetting the number of months
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
    customer_arr_df, metrics_df = create_customer_and_aggregated_metrics(transposed_df)

    return customer_arr_df, metrics_df



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
    - pd.DataFrame: Gives aggregated metrics  - MRR, ARR, newBusiness, upSell, downSell, churn 
    """


    df.insert(2, 'measureType', 'monthlyRevenue')

    # Identify 'newBusiness' rows based on the condition
    mask = (df.shift(axis=1, fill_value=0) == 0) & (df != 0)

    # Create a new DataFrame with 'newBusiness' rows
    new_business_df = df[mask].copy()
    new_business_df['measureType'] = 'newBusiness'

    # Fill NaN values with 0
    new_business_df = new_business_df.fillna(0)

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

    df_agg = annualize_agg_arr(df_agg)

    df_agg = transalte_columns(df_agg)

    return df_rr, df_agg


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

    print(waterfall_df)
    # Shift the columns of the original df - by one colmn- and add it  to waterfall df - so that it now captures last month's revenue
    waterfall_df.iloc[0, 2:] = df.iloc[0, 1:-1].values

    print(waterfall_df)

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


def sort_by_first_month_of_sales(df): 
    """
    Sort the df containing monthwise customer revenue grid, in the order of first month of sale

    Parameters:
    - df (pd.DataFrame): Dataframe with monthwise customer revenue grid

    Returns:
    - pd.DataFrame: Same grid but sorted in first month of sales 
    """

    # assumes the first 3 columns are customerId, customerName, and measureType

    # Create a new column 'first_non_zero_month' to store the name of the first non-zero sales month
    df['first_non_zero_month'] = (df.iloc[:, 3:] != 0).idxmax(axis=1)

    # Create a new column 'last_non_zero_month' to store the name of the last non-zero sales month
    df['last_non_zero_month'] = (df.iloc[:, 3:-1].apply(lambda x: x.iloc[::-1].ne(0).idxmax() if x.any() else 'NaN', axis=1))

    # 'first_non_zero_month', 'last_non_zero_month', and finally by 'customerId'
    sorted_df = df.sort_values(by=[ 'first_non_zero_month', 'last_non_zero_month', 'customerId'])

    # Reset the index if needed
    sorted_df.reset_index(drop=True, inplace=True)

    # Drop the 'first_non_zero_month' and 'last_non_zero_month' columns
    sorted_df.drop(columns=['first_non_zero_month', 'last_non_zero_month'], inplace=True)

    return sorted_df


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

def transalte_columns(df):
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

def reconcile_overrides(scratch_pad_df, override_df ):
    """
    Compares the scratchpad and override dfs - and create a recon_df with the difference in values for a given customer and month

    Parameters:
    - scratch_pad_df (pd.DataFrame): scratch pad df 
    - override_df  (pd.DataFrame): override df 

    Returns:
    - pd.DataFrame: for each customer as row and months as columns, it creates the differnce between the tow input dfs 
    """

    # Replace NaN values with zeros in both DataFrames
    scratch_pad_df.fillna(0, inplace=True)
    override_df.fillna(0, inplace=True)


    # Melt the DataFrames to convert months into rows
    melted_df_edited = pd.melt(scratch_pad_df, id_vars=['customerId', 'customerName'], var_name='month', value_name='value_edited')
    melted_df_override = pd.melt(override_df, id_vars=['customerId', 'customerName'], var_name='month', value_name='value_override')

    # Merge the melted DataFrames on 'customerId', 'customerName', and 'month'
    merged_df = melted_df_edited.merge(melted_df_override, on=['customerId', 'customerName', 'month'], how='outer')

    # Calculate the differences for each row using vectorized operations
    merged_df['difference'] =  merged_df['value_override'].fillna(0) - merged_df['value_edited'].fillna(0)

    # Create a new DataFrame containing 'customerId', 'customerName', 'month', and 'difference'
    result_df = merged_df[['customerId', 'customerName', 'month', 'difference']]

    # Sort the result DataFrame by 'customerId' and 'month'
    result_df.sort_values(by=['customerId', 'month'], inplace=True)

    # Transpose the result DataFrame to make months become columns
    transposed_result_df = result_df.pivot_table(index=['customerId', 'customerName'], columns='month', values='difference', fill_value=0).reset_index()

    # Remove the month as index 
    transposed_result_df.columns.name = None  # Remove the 'month' label

    # Drop rows where all columns except 'customerId' and 'customerName' have a value of 0
    transposed_result_df = transposed_result_df[(transposed_result_df.drop(['customerId', 'customerName'], axis=1) != 0).any(axis=1)]

    return transposed_result_df

