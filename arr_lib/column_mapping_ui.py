import streamlit as st
import pandas as pd
from arr_lib.column_mapping import map_columns
from arr_lib.arr_validations import validate_input_data
from arr_lib.arr_validations import validate_mapping
import os


# column mapper with dateformat picker
def perform_column_mapping(predefined_columns, predefined_date_formats, input_df):


    # Column names from the DataFrame
    column_names = list(input_df.columns)

    # file_path for saving the mapping 
    saved_map_file_path = os.path.join('saved_map', 'column_map.csv')

    # empty_df to return is the status being returned is False 
    empty_df = pd.DataFrame()

    if 'mapped_df' not in st.session_state:
        st.session_state.mapped_df = pd.DataFrame()

    if 'column_mapping_status' not in st.session_state:
        st.session_state.column_mapping_status = False
    

    # Create a DataFrame
    df = pd.DataFrame({'columnHeaders': predefined_columns, 'columnNames': 'double click to select .. ', 'dateFormat': 'pick appropriate date format'})
    print(df)

    # populate the df from session if exists 

    if 'loaded_map_df' not in st.session_state:
        st.session_state.loaded_map_df = pd.DataFrame()
    else: 
        loaded_map_df = st.session_state.loaded_map_df
        if (not loaded_map_df.empty): 
                    df = loaded_map_df


    # Initialize the mapping dictionary in session state
    if 'column_mapping' not in st.session_state:
        st.session_state.column_mapping = {}

    st.subheader("Map columns", divider='green')    

    col1a, col2a, col3a, col4a = st.columns([1,2,2,3], gap="small")
    with col2a: 
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Load Column Map"):
            try:
                loaded_map_df = pd.read_csv(saved_map_file_path)
                st.session_state.loaded_map_df = loaded_map_df
                # st.success(f"Saved map loaded")

                loaded_map_df = st.session_state.loaded_map_df

                if (not loaded_map_df.empty): 
                    df = loaded_map_df

            except FileNotFoundError:
                st.error(f"File '{saved_map_file_path}' not found. Please save the DataFrame first.")


    col1, col2, col3 = st.columns([1,6,1], gap="small")
    with col2: 

        st.markdown(f"<br><p class='md_med'>Map the columns of your input file to specific data elements defined in the app</p>", unsafe_allow_html=True)
        
        result_df= st.data_editor(
            df, 
            column_config={
                "columnNames": st.column_config.SelectboxColumn(
                    "Columns in File",
                    help="The category of the app",
                    width="medium",
                    options=column_names,
                    required=True,
                ), 
                "columnHeaders": st.column_config.TextColumn(
                    "Application Data Element",
                    disabled=True,
                ), 
                "dateFormat" : st.column_config.SelectboxColumn(
                    "Date Format",
                    width="meadium",
                    options=predefined_date_formats,
                )
            }, 
            hide_index=True,
            )
        st.session_state.result_df = result_df

    with col3a:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button('Save Column Map'):
            result_df.to_csv(saved_map_file_path, index=False)
            st.success(f"Column mapped saved")

    with col2:

        result_df = st.session_state.result_df
       
        if st.button('  Map Uploaded Data  '):
            
            # Validate that the mapping is complete 
            valid_map = validate_mapping(column_names, predefined_date_formats, result_df)
            if not valid_map : 
                if 'column_mapping_status' not in st.session_state:
                    st.session_state.column_mapping_status = False
                return empty_df, False; 
        
            # change the column header of the input_df based on mapped column
            if result_df is not None:
                mapped_df = map_columns (input_df, result_df)
                st.session_state.mapped_df = mapped_df

                validation_status = validate_input_data(st.session_state.mapped_df)
                st.session_state.column_mapping_status = validation_status

            return st.session_state.mapped_df, st.session_state.column_mapping_status
        else: 
            # # initialize validation status
            if 'column_mapping_status' not in st.session_state:
                    st.session_state.column_mapping_status = False
            return st.session_state.mapped_df, st.session_state.column_mapping_status
