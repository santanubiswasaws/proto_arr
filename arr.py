import streamlit as st
import pandas as pd
from arr_lib.setup import PREDEFINED_COLUMN_HEADERS
from arr_lib.setup import PREDEFINED_DATE_FORMATS
from arr_lib.arr_analysis import create_monthly_buckets
from arr_lib.arr_analysis import create_arr_metrics
from arr_lib.arr_analysis import create_customer_and_aggregated_metrics
from arr_lib.column_mapping_ui import perform_column_mapping
from arr_lib.styling import BUTTON_STYLE

# on_change callback for file upload 
def clear_session_cb ():
    for key in st.session_state.keys():
        del st.session_state[key]

def main():

    st.set_page_config(page_title="ARR Analysis" , layout='wide')
    st.header("Analyze Annual Recurring Revnue (ARR)")


    st.markdown(BUTTON_STYLE, unsafe_allow_html=True)

    # Upload CSV file
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], on_change = clear_session_cb)

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)


        # Display mapped data 
        with st.expander('Show/Hide uploaded data', expanded=True):
            st.subheader('Uploaded Data :', divider='green') 
            st.write(df)

        st.markdown("<br>", unsafe_allow_html=True)


        # Column Mapping Section 

        # initialize mapped_df
        if 'mapped_df' not in st.session_state:
                st.session_state.mapped_df = pd.DataFrame()
        # # initialize validation status
        if 'column_mapping_status' not in st.session_state:
                st.session_state.column_mapping_status = False

        # Map file column names based on mapped columns and validate content     
        #if not st.session_state.column_mapping_status: 
        with st.expander('Show/Hide Column mapping', expanded=True):
            mapped_df, column_mapping_status = perform_column_mapping(PREDEFINED_COLUMN_HEADERS, PREDEFINED_DATE_FORMATS, df)  
            st.session_state.column_mapping_status = column_mapping_status
            st.session_state.mapped_df =  mapped_df

        # else:
        mapped_df = st.session_state.mapped_df
        
        # Display mapped uploaded data 
        if (not mapped_df.empty) and st.session_state.column_mapping_status:

            # Display mapped data 
            with st.expander('Show/Hide mapped data', expanded=True):
                st.subheader("Mapped Data :", divider='green') 
                st.dataframe(st.session_state.mapped_df, use_container_width=False)

        st.markdown("<br><br>", unsafe_allow_html=True)

        # initialize monthly_bucket_df 
        if 'monthly_bucket_df' not in st.session_state:
                st.session_state.monthly_bucket_df = pd.DataFrame()

        # Add a button to generate ARR metrics 
        if 'generate_arr_metrics_button_clicked' not in st.session_state:
            st.session_state.generate_arr_metrics_button_clicked = False

        # Initialize customer and aggregate level dfs 
        if 'transpose_df' not in st.session_state:
                st.session_state.transpose_df = pd.DataFrame(columns=['customerId', 'measureType'])
        if 'metrics_df' not in st.session_state:
                st.session_state.metrics_df = pd.DataFrame(columns=['customerId', 'measureType'])

        if (not mapped_df.empty) and st.session_state.column_mapping_status: 
                st.session_state.generate_arr_metrics_button_clicked = st.button("Generate ARR Analysis", type="primary")

        if  st.session_state.generate_arr_metrics_button_clicked and st.session_state.column_mapping_status:
            try:
                with st.spinner("Generating ARR  Analytics ..."):

                    # Step 1: Generate monthly buckets
                    # -------
                    mapped_df = st.session_state.mapped_df
                    monthly_bucket_df = create_monthly_buckets(mapped_df)                    
                    st.session_state.monthly_bucket_df = monthly_bucket_df

                    # Step 2: Create transposed matrix with arr details and aggregated arr metrics
                    # -------                    
                    transpose_df, metrics_df = create_arr_metrics(monthly_bucket_df)
         
                    st.session_state.transpose_df = transpose_df
                    st.session_state.metrics_df = metrics_df

            except ValueError as e:
                st.error(f"Error: {str(e)}")

        # Step 3: Display transposed customer level and aggregated metrics
        # -------
        metrics_df = st.session_state.metrics_df
        if (not metrics_df.empty) and st.session_state.column_mapping_status:
            
            # Display customer level detailes 
            with st.expander('Show/Hide customer level ARR details', expanded = True):

                st.subheader('Customer Level ARR Metrics :', divider='green') 

                # set inde to customerId, measureType - for freeze pane functionality
                display_transposed_df = st.session_state.transpose_df.round(2)
                display_transposed_df.set_index(['customerId'], inplace=True)
                st.dataframe(display_transposed_df, use_container_width=True)

            st.subheader('Aggregated ARR Metrics :', divider='green') 

            # set index to customerId, measureType - for freeze pane functionality
            display_metrics_df= st.session_state.metrics_df.round(0)
            display_metrics_df.set_index(['customerId', 'measureType'], inplace=True)
            st.dataframe(display_metrics_df, use_container_width=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)


        # Step 4: Generate Scratchpad 
        # -----
        if 'planning_df' not in st.session_state:
                st.session_state.planning_df = pd.DataFrame(columns=['customerId', 'measureType'])

        if "random_key" not in st.session_state:
            st.session_state["random_key"] = 0

        if 'create_reset_planning_sheet_button_clicked' not in st.session_state:
                st.session_state.create_reset_planning_sheet_button_clicked = False

        if 'metrics_df' not in st.session_state:
            st.session_state.metrics_df = pd.DataFrame(columns=['customerId', 'measureType'])
        metrics_df = st.session_state.metrics_df

        if st.session_state.column_mapping_status and (not metrics_df.empty): 
             st.session_state.create_reset_planning_sheet_button_clicked = st.button("Create or Reset Planing Sheet", type="primary")

        if st.session_state.create_reset_planning_sheet_button_clicked and st.session_state.column_mapping_status:       
            st.session_state["random_key"] += 1   
            try:
                with st.spinner("Creating planning sheet"):
                    
                    #reset panning_df 
                    if 'planning_df' in st.session_state:
                        st.session_state.planning_df = pd.DataFrame(columns=['customerId', 'measureType'])

                    # Call the method to create the metrics df
                    planning_df = st.session_state.transpose_df
                    planning_df = planning_df[planning_df['measureType'] == 'monthlyRevenue']      
                    st.session_state.planning_df = planning_df

                    # reset replan output dfs 
                    st.session_state.replan_metrics_df = pd.DataFrame()
                    st.session_state.replan_transpose_df = pd.DataFrame()

            except ValueError as e:
                st.error(f"Error: {str(e)}")

        planning_df = st.session_state.planning_df
        if (not planning_df.empty) and st.session_state.column_mapping_status: 
            # Display planning scratchpad        
            st.subheader('Planning scratchpad - you can edit :', divider='green') 
            try:

                # set inde to customerId - for freeze pane functionality
                display_planning_df = st.session_state.planning_df.round(2)
                display_planning_df.set_index(['customerId'], inplace=True)
                # edited_df = st.data_editor(display_planning_df, key=st.session_state["random_key"], disabled=('customerId', 'measureType'), num_rows='dynamic', hide_index=False, use_container_width=True)
                edited_df = st.data_editor(display_planning_df, key=st.session_state["random_key"], num_rows='dynamic', hide_index=False, use_container_width=True)
                
                # reset index to numeric value 
                edited_df.reset_index(inplace=True)
                st.session_state.edited_df = edited_df
            except Exception as e:
                    st.error(f"An error occurred: {e}") 

        st.markdown("<br>", unsafe_allow_html=True)


        # Step 5: Replanning ARR section 
        # ------

        if 'replan_transpose_df' not in st.session_state:
                st.session_state.replan_transpose_df= pd.DataFrame(columns=['customerId', 'measureType'])

        if 'replan_metrics_df' not in st.session_state:
                st.session_state.replan_metrics_df = pd.DataFrame(columns=['customerId', 'measureType'])

        if 'replan_arr_metrics_button_clicked' not in st.session_state:
                st.session_state.replan_arr_metrics_button_clicked = False

        if 'edited_df' not in st.session_state:
                st.session_state.edited_df = pd.DataFrame()

        edited_df = st.session_state.edited_df 
        if (not edited_df.empty) and st.session_state.column_mapping_status: 
             st.session_state.replan_arr_metrics_button_clicked = st.button("Replan ARR", type="primary")

        # Add a button to calculate monthly contract values
        if st.session_state.replan_arr_metrics_button_clicked and st.session_state.column_mapping_status:        
            try:
                with st.spinner("Replanning ARR Metrics"):
                    
                    # Call the method to create the metrics df
                    edited_df = st.session_state.edited_df
                    
                    replan_transpose_df, replan_metrics_df = create_customer_and_aggregated_metrics(edited_df)

                    st.session_state.replan_transpose_df = replan_transpose_df
                    st.session_state.replan_metrics_df = replan_metrics_df
                    
            except ValueError as e:
                st.error(f"Error: {str(e)}")

        replan_metrics_df = st.session_state.replan_metrics_df 
        if (not replan_metrics_df.empty) and st.session_state.column_mapping_status:  
            # Display customer level detailes 

            with st.expander('Show/Hide customer level replan details', expanded = True):
                st.subheader('Replanned Customer Level ARR Metrics :', divider='green') 

                # set inde to customerId, measureType - for freeze pane functionality
                display_replan_transpose_df = st.session_state.replan_transpose_df.round(2)
                display_replan_transpose_df.set_index(['customerId'], inplace=True)
                st.dataframe(display_replan_transpose_df, use_container_width=True)

            st.subheader('Replanned Aggregated ARR Metrics :', divider='green') 

            # set inde to customerId, measureType - for freeze pane functionality
            display_replan_metrics_df = st.session_state.replan_metrics_df.round(0)
            display_replan_metrics_df.set_index(['customerId', 'measureType'], inplace=True)
            st.dataframe(display_replan_metrics_df, use_container_width=True)


    # -- Create sidebar for plot controls
    st.sidebar.title('AI helper')
    query= st.sidebar.text_area('Ask your question - not implemented yet')
    st.sidebar.button(label="Ask - not functional yet - @todo")

if __name__ == "__main__":
    main()


