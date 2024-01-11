import pandas as pd
from datetime import datetime
import streamlit as st

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
    # # Check if the required columns are present
    # required_columns = ['customerId', 'contractId', 'contractStartDate', 'contractEndDate', 'totalContractValue']
    # if not all(col in df.columns for col in required_columns):
    #     raise ValueError("Columns 'customerId', 'contractId', 'contractStartDate', 'contractEndDate', and 'totalContractValue' are required in the DataFrame.")

    # # Validate date formats in 'contractStartDate' and 'contractEndDate'
    # try:
    #     df['contractStartDate'] = pd.to_datetime(df['contractStartDate'], format='%m/%d/%y')
    #     df['contractEndDate'] = pd.to_datetime(df['contractEndDate'], format='%m/%d/%y')
    # except ValueError:
    #     raise ValueError("Invalid date format in 'contractStartDate' or 'contractEndDate'. Use 'mm/dd/yy' format.")

    # # Calculate the contract duration in months
    # df['contractDuration'] = (df['contractEndDate'] - df['contractStartDate']).dt.days 

    # # Validate contract duration
    # valid_contract_duration = df['contractDuration'] > 0
    # if not valid_contract_duration.all():
    #     raise ValueError("Invalid contract duration. 'contractEndDate' should be later than 'contractStartDate'.")
    
    # # Validate contract value column
    # if not pd.to_numeric(df['totalContractValue'], errors='coerce').notna().all():
    #     raise ValueError("Invalid 'totalContractValue'. It must contain numeric values.")
    
    # # Calculate contractLength in terms of days
    # df['contractLength'] = (df['contractEndDate'] - df['contractStartDate']).dt.days

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
    second_df = second_df[['customerId', 'contractId', 'month', 'monthlyRevenue']]

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
    df = df.loc[:, ['customerId', 'month','monthlyRevenue']]

    # Melt the original dataframe
    melted_df = pd.melt(df, id_vars=['customerId', 'month'],
                        var_name='measureType', value_name='value')

    print("melted df")
    #print(melted_df)
    # Get unique months dynamically
    # Transpose the melted dataframe
    transposed_df = melted_df.pivot_table(index=['customerId', 'measureType'],
                                        columns='month', values='value', fill_value=0, aggfunc='sum').reset_index()

    #print(transposed_df)
    # Rename the columns for better clarity
    transposed_df.columns.name = None  # Remove the 'month' label

    # Display the transposed dataframe
    print("\nTransposed DataFrame:")
    print(transposed_df)

    return transposed_df

def create_aggregated_arr_metrics(df):
    """
    Process df containing transposed monthly metrics for each customer, aggregates the values for all customers and returns the aggregated df

    Parameters:
    - df (pd.DataFrame): transposed monthly metrics for each customerlevel with revenue, new buessiness, upsell, downsell and churn

    Returns:
    - pd.DataFrame: Gives the over all metrics for each month - MRR, ARR, newBusiness, upSell, downSell, churn 
    """


    # Group by 'customerId' and aggregate the sum across all measureTypes for each month

    aggregated_df = df.groupby(['measureType'], observed=True).agg({col: 'sum' for col in df.columns[2:]}).reset_index()

    aggregated_df.insert(0, 'customerId', 'Aggregated')


    # # Add a new row for 'ARR' which is 12 * monthlyRevenue
    arr_row = pd.DataFrame({
        'customerId': ['Aggregated'],
        'measureType': ['ARR']})
    
    # Calculate values for each month
    values_dict = {
        month: 12 * aggregated_df.loc[aggregated_df['measureType'] == 'monthlyRevenue', month].iloc[0]
        for month in df.columns[2:]
    }

    # Create a Series with the calculated values and set the index to match df.columns
    arr_series = pd.Series(values_dict, index=df.columns[2:])

    # # Append the new row to the DataFrame
    # arr_series = pd.Series(values_dict, index=df.columns[2:])

    # Create a DataFrame from the Series
    arr_row = pd.DataFrame([arr_series], columns=arr_series.index)

    # Add 'customerId' and 'measureType'
    arr_row['customerId'] = 'Aggregated'
    arr_row['measureType'] = 'ARR'

    # add the ARR row to the original df 
    aggregated_df = pd.concat([aggregated_df, arr_row], ignore_index=True)

    # Display the aggregated DataFrame
    print("\nAggregated DataFrame:")
    print(aggregated_df)

    return aggregated_df


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

    # Identify 'downSell' rows based on the condition for all month columns
    down_sell_mask = (df_numeric.diff(axis=1) < 0) & (df_numeric.shift(axis=1) != 0) & (df_numeric !=0 )
    down_sell_df = (df_numeric[down_sell_mask] - df_numeric.shift(axis=1))[down_sell_mask].copy()
    down_sell_df['measureType'] = 'downSell'

    # Retrieve the 'customerId' values for 'downSell' rows
    down_sell_df['customerId'] = df.loc[down_sell_mask.index, 'customerId'].values

    # Calculate 'churn' rows based on the specified condition
    churn_mask = (df_numeric.diff(axis=1) < 0) & (df_numeric == 0)
    churn_df = (df_numeric[churn_mask] - df_numeric.shift(axis=1))[churn_mask].copy()
    churn_df['measureType'] = 'churn'


    # Retrieve the 'customerId' values for 'churn' rows
    churn_df['customerId'] = df.loc[churn_mask.index, 'customerId'].values

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
    df = df.sort_values(['customerId', 'measureType'])


    df_agg = create_aggregated_arr_metrics(df)

    # convert the aggregated df to a waterfall structure
    df_agg = create_waterfall(df_agg)

    # select only the monthlyRevenue for csutomer level details 
    df_rr = df[df['measureType'] == 'monthlyRevenue']


    # sort mothly_revenue matrix, but first month of sales

    df_rr = sort_by_first_month_of_sales(df_rr)

    print(df)

    return df_rr, df_agg


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

    # Create a copy of the DataFrame for the waterfall version
    waterfall_df = df[df['measureType']=='monthlyRevenue'].copy()

    # Shift the columns to calculate 'lastMonthRevenue'
    waterfall_df.iloc[0, 3:] = df.iloc[0, 2:-1].values

    # rename the row measureType 
    waterfall_df.iloc[0, 1] = "lastMonthRevenue"

    # concat the lastMonthrevenue to to the df
    waterfall_df = pd.concat([waterfall_df, df], ignore_index=True)

    # Define the sorting order for 'measureType'
    sorting_order = ['lastMonthRevenue', 'newBusiness', 'upSell', 'downSell', 'churn', 'monthlyRevenue', 'ARR']

    # Sort the DataFrame based on 'measureType' using the defined order and 'customerId'
    waterfall_df['measureType'] = pd.Categorical(waterfall_df['measureType'], categories=sorting_order, ordered=True)
    waterfall_df = waterfall_df.sort_values(['customerId', 'measureType'])


    return waterfall_df


def sort_by_first_month_of_sales(df): 
    """
    Sort the df containing monthwise customer revenue grid, in the order of first month of sale

    Parameters:
    - df (pd.DataFrame): Dataframe with monthwise customer revenue grid

    Returns:
    - pd.DataFrame: Same grid but sorted in first month of sales 
    """

    # assumes the first two columns are customerId and measureType

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


