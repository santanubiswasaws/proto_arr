import pandas as pd
import streamlit as st 


# returns a new dataframe with the column header names changed as per the column mapping performed by the user
@st.cache_data
def map_columns(df, column_mapping_df):
    """
    Map columns in the DataFrame according to the provided mapping.

    Parameters:
    - df (pd.DataFrame): Original DataFrame.
    - column_mapping (dict): Dictionary mapping predefined columns to user-selected columns.

    Returns:
    - pd.DataFrame: DataFrame with columns mapped according to the provided mapping.
    """

    column_mapping = column_mapping_df.set_index('columnHeaders')['columnNames'].to_dict()

    new_df = pd.DataFrame({key: df[value].tolist() for key, value in column_mapping.items()})

    st_format = column_mapping_df.loc[column_mapping_df['columnHeaders']=='contractStartDate', 'dateFormat'].iloc[0]
    end_format =  column_mapping_df.loc[column_mapping_df['columnHeaders'] == 'contractEndDate', 'dateFormat'].iloc[0]

    new_df['startDateFormat'] = st_format
    new_df['endDateFormat'] = end_format

    return new_df


