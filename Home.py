import streamlit as st
import pandas as pd
from arr_lib.setup import PREDEFINED_COLUMN_HEADERS
from arr_lib.setup import PREDEFINED_DATE_FORMATS
from arr_lib.arr_analysis import create_monthly_buckets
from arr_lib.arr_analysis import create_arr_metrics
from arr_lib.arr_analysis import create_customer_and_aggregated_metrics
from arr_lib.arr_analysis import reconcile_overrides
from arr_lib.arr_analysis import highlight_positive_negative_cells, decorate_logo_metrics_df
from arr_lib.arr_analysis import apply_overrides
from arr_lib.arr_analysis import stylize_metrics_df, rename_columns
from arr_lib.column_mapping_ui import perform_column_mapping
from arr_lib.styling import BUTTON_STYLE
from arr_lib.styling import MARKDOWN_STYLES
from arr_lib.styling import GLOBAL_STYLING

# on_change callback for file upload 
def clear_session_cb ():
    for key in st.session_state.keys():
        del st.session_state[key]

def main():

    st.set_page_config(page_title="ARR Analysis" , layout='wide')
    st.header("Analyze Annual Recurring Revnue (ARR)")


    st.markdown(BUTTON_STYLE, unsafe_allow_html=True)
    st.markdown(MARKDOWN_STYLES, unsafe_allow_html=True)
    st.markdown(GLOBAL_STYLING, unsafe_allow_html=True)

    # Initialize file upload details 
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
        st.session_state.df = pd.DataFrame()
        print('getting wiped')

    # upload files
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], on_change = clear_session_cb)
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state.df = df
        st.session_state.uploaded_file = uploaded_file       
  
    # Conitnue processing is uploaded data is available 
    df = st.session_state.df
    if not df.empty:
        # Display mapped data 
        with st.expander('Show/Hide uploaded data', expanded=True):
            st.subheader('Uploaded Data :', divider='green') 
            st.write(df)

        st.markdown("<br>", unsafe_allow_html=True)


        # -------------------------------------------------------------------------------
        # Step 1: Column Mapping Section 
        # -------------------------------------------------------------------------------

        # initialize mapped_df
        if 'mapped_df' not in st.session_state:
                st.session_state.mapped_df = pd.DataFrame()
        # # initialize validation status
        if 'column_mapping_status' not in st.session_state:
                st.session_state.column_mapping_status = False

        # Map file column names based on mapped columns and validate content     
        with st.expander('Show/Hide Column mapping', expanded=True):
            mapped_df, column_mapping_status = perform_column_mapping(PREDEFINED_COLUMN_HEADERS, PREDEFINED_DATE_FORMATS, df)  
            st.session_state.column_mapping_status = column_mapping_status
            st.session_state.mapped_df =  mapped_df

        mapped_df = st.session_state.mapped_df


        # -------------------------------------------------------------------------------        
        # Step 2: Display mapped uploaded data 
        # -------------------------------------------------------------------------------

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
            
        if 'cust_arr_waterfall_df' not in st.session_state:
                st.session_state.cust_arr_waterfall_df = pd.DataFrame(columns=['customerId', 'measureType'])            
        if 'customer_arr_df' not in st.session_state:
                st.session_state.customer_arr_df = pd.DataFrame(columns=['customerId', 'measureType'])
        if 'logo_metrics_df' not in st.session_state:
                st.session_state.logo_metrics_df = pd.DataFrame(columns=['customerId', 'measureType'])
        if 'metrics_df' not in st.session_state:
                st.session_state.metrics_df = pd.DataFrame(columns=['customerId', 'measureType'])

        if (not mapped_df.empty) and st.session_state.column_mapping_status: 
                st.session_state.generate_arr_metrics_button_clicked = st.button("Generate ARR Analysis", type="primary")

        if  st.session_state.generate_arr_metrics_button_clicked and st.session_state.column_mapping_status:
            try:
                with st.spinner("Generating ARR  Analytics ..."):

                    # Step 2a: Generate monthly buckets
                    # ----------------------------------
                    mapped_df = st.session_state.mapped_df
                    monthly_bucket_df = create_monthly_buckets(mapped_df)                    
                    st.session_state.monthly_bucket_df = monthly_bucket_df

                    # Step 2b: Create transposed matrix with arr details and aggregated arr metrics
                    #---------------------------------------------------------------------------------                   
                    cust_arr_waterfall_df, customer_arr_df, logo_metrics_df, metrics_df = create_arr_metrics(monthly_bucket_df)

                    st.session_state.customer_arr_waterfall_df = cust_arr_waterfall_df         
                    st.session_state.customer_arr_df = customer_arr_df
                    st.session_state.logo_metrics_df = logo_metrics_df
                    st.session_state.metrics_df = metrics_df

            except ValueError as e:
                st.error(f"Error: {str(e)}")


        # -------------------------------------------------------------------------------                
        # Step 3: Display transposed customer level and aggregated metrics
        # -------------------------------------------------------------------------------   
                
        metrics_df = st.session_state.metrics_df
        if (not metrics_df.empty) and st.session_state.column_mapping_status:
            
            # Display customer level detailes 
            with st.expander('Show/Hide MRR by Customer', expanded = True):
                st.subheader('MRR by Customer :', divider='green') 
                # set index to customerId, measureType - for freeze pane functionality
                display_customer_arr_df = st.session_state.customer_arr_df.round(2)
                display_customer_arr_df.set_index(['customerName'], inplace=True)
                st.dataframe(display_customer_arr_df, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Display customer count detailes 
            with st.expander('Show/Hide Customer Count', expanded = True):
                st.subheader('Customer Count :', divider='green') 
                # set inde to measureType
                display_logo_metrics_df = rename_columns(st.session_state.logo_metrics_df.round(0))
                display_logo_metrics_df.set_index(['measureType'], inplace=True)

                display_logo_metrics_df = decorate_logo_metrics_df(display_logo_metrics_df)
                st.dataframe(display_logo_metrics_df, use_container_width=True)


            st.subheader('ARR Walk (by Type) :', divider='green') 


            # Stylize aggregated metrics DF
            display_metrics_df= stylize_metrics_df(st.session_state.metrics_df)

            st.dataframe(display_metrics_df, use_container_width=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)


        # -------------------------------------------------------------------------------
        # Step 4a: Override section 
        # -------------------------------------------------------------------------------

        if 'uploaded_override_file' not in st.session_state:
            st.session_state.uploaded_override_file = None

        if 'override_df' not in st.session_state:
            st.session_state.override_df = pd.DataFrame()

        if 'recon_df' not in st.session_state:
            st.session_state.recon_df = pd.DataFrame()

        if (not metrics_df.empty) and st.session_state.column_mapping_status: 
            st.subheader('Import Historical MRR data (optional)  :', divider='green') 
            uploaded_override_file = st.file_uploader("Upload historical MRR data - it must contain CustomerID and CustomerName Columns",type=["csv"])   
            st.session_state.uploaded_override_file = uploaded_override_file

        uploaded_override_file = st.session_state.uploaded_override_file
        if uploaded_override_file is not None:
            override_df = pd.read_csv(uploaded_override_file)
            st.session_state.override_df = override_df

        override_df =  st.session_state.override_df 
        if (not override_df.empty):    
            try:
                with st.expander('Show/Hide uploaded historical details', expanded = True):
                    st.subheader('Uploaded historical details :', divider='green')     
                    display_override_df = override_df.round(2)
                    display_override_df.set_index(['customerName'], inplace=True)
                    st.dataframe(display_override_df)
            except Exception as e:
                st.error(f"Error: {e}") 

        if (not override_df.empty ) and (not metrics_df.empty) and st.session_state.column_mapping_status: 
            try: 
                recon_df = reconcile_overrides(st.session_state.customer_arr_df, st.session_state.override_df)
                st.session_state.recon_df = recon_df
                with st.expander('Show/Hide MRR reconciliation between imported and historical data', expanded = True):
                    st.subheader('MRR reconciliation between imported and historical data :', divider='green')  
                    display_recon_df = recon_df.round(0)   
                    display_recon_df.set_index(['customerName', 'customerId'], inplace=True)  
                    display_recon_df = highlight_positive_negative_cells(display_recon_df)   
                    display_recon_df = display_recon_df.format("{:,.2f}")      
                    st.dataframe(display_recon_df) 
            except Exception as e:
                st.error(f"Error: {e}") 


        # -------------------------------------------------------------------------------
        # 4b. Display options for applying override
        # -------------------------------------------------------------------------------

        if 'apply_override' not in st.session_state:
            st.session_state.apply_override = None 
             

        if (not override_df.empty ) and (not metrics_df.empty) and st.session_state.column_mapping_status:        
            st.session_state.apply_override = st.checkbox('Apply Override', st.session_state.apply_override)


        # -------------------------------------------------------------------------------
        # Step 5: Generate Scratchpad 
        # -------------------------------------------------------------------------------
                
        st.markdown("<br><br>", unsafe_allow_html=True)

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
             st.session_state.create_reset_planning_sheet_button_clicked = st.button("Edit MRR by Customer data", type="primary")

        if st.session_state.create_reset_planning_sheet_button_clicked and st.session_state.column_mapping_status:       
            st.session_state["random_key"] += 1   
            try:
                with st.spinner("Creating planning sheet"):
                    
                    #reset panning_df 
                    if 'planning_df' in st.session_state:
                        st.session_state.planning_df = pd.DataFrame()

                    
                    # Call the method to create the metrics df
                    if st.session_state.apply_override: 
                         planning_df = apply_overrides(st.session_state.customer_arr_df, st.session_state.override_df)
                    else:
                        planning_df = st.session_state.customer_arr_df  
                    st.session_state.planning_df = planning_df

                    # reset replan output dfs 
                    st.session_state.replan_metrics_df = pd.DataFrame()
                    st.session_state.replan_customer_arr_df = pd.DataFrame()

            except ValueError as e:
                st.error(f"Error: {str(e)}")

        planning_df = st.session_state.planning_df
        if (not planning_df.empty) and st.session_state.column_mapping_status: 

            # Display planning scratchpad        
            # st.subheader('Planning scratchpad :', divider='green') 
 
            try:

                st.markdown(f"<br><p class='md_big'>Edit MRR data if needed (directly in the table below or use csv/excel and copy/paste)</p>", unsafe_allow_html=True)
                # set index to customerName - for freeze pane functionality
                display_planning_df = st.session_state.planning_df.round(2)
                display_planning_df.set_index(['customerName'], inplace=True)
                # edited_df = st.data_editor(display_planning_df, key=st.session_state["random_key"], disabled=('customerId', 'measureType'), num_rows='dynamic', hide_index=False, use_container_width=True)
                edited_df = st.data_editor(display_planning_df, key=st.session_state["random_key"], num_rows='dynamic', hide_index=False, use_container_width=True)
                
                # reset index to numeric value 
                edited_df.reset_index(inplace=True)
                st.session_state.edited_df = edited_df
            except Exception as e:
                    st.error(f"An error occurred: {e}") 
        st.markdown("<br>", unsafe_allow_html=True)


        # -------------------------------------------------------------------------------                                 
        # Step 6: Generate replanned ARR metrics 
        # -------------------------------------------------------------------------------
            
        st.markdown("<br>", unsafe_allow_html=True)


        if 'replan_customer_arr_waterfall_df' not in st.session_state:
                st.session_state.replan_customer_arr_waterfall_df= pd.DataFrame(columns=['customerId', 'measureType'])

        if 'replan_customer_arr_df' not in st.session_state:
                st.session_state.replan_customer_arr_df= pd.DataFrame(columns=['customerId', 'measureType'])

        if 'replan_logo_metrics_df' not in st.session_state:
                st.session_state.replan_logo_metrics_df= pd.DataFrame(columns=['customerId', 'measureType'])

        if 'replan_metrics_df' not in st.session_state:
                st.session_state.replan_metrics_df = pd.DataFrame(columns=['customerId', 'measureType'])

        if 'replan_arr_metrics_button_clicked' not in st.session_state:
                st.session_state.replan_arr_metrics_button_clicked = False

        if 'edited_df' not in st.session_state:
                st.session_state.edited_df = pd.DataFrame()

        # Add a button to calculate monthly contract values
        call_edited_df = st.session_state.edited_df 
        if (not call_edited_df.empty) and st.session_state.column_mapping_status: 
             st.session_state.replan_arr_metrics_button_clicked = st.button("View Final MRR by Customer and Customer/ARR Metrics", type="primary")

        if st.session_state.replan_arr_metrics_button_clicked and st.session_state.column_mapping_status:        
            try:
                with st.spinner("Replanning ARR Metrics"):
                    
                    # Call the method to create the metrics df
                    call_edited_df = st.session_state.edited_df     
         
                    replan_customer_arr_waterfall_df, replan_customer_arr_df, replan_logo_metrics_df, replan_metrics_df = create_customer_and_aggregated_metrics(call_edited_df)

                    st.session_state.replan_customer_arr_waterfall_df = replan_customer_arr_waterfall_df
                    st.session_state.replan_customer_arr_df = replan_customer_arr_df  
                    st.session_state.replan_logo_metrics_df = replan_logo_metrics_df
                    st.session_state.replan_metrics_df = replan_metrics_df

            except ValueError as e:
                st.error(f"Error: {str(e)}")


        # -------------------------------------------------------------------------------                                 
        # Step 6b: Dispay replanned ARR 
        # -------------------------------------------------------------------------------

        replan_metrics_df = st.session_state.replan_metrics_df 
        if (not replan_metrics_df.empty) and st.session_state.column_mapping_status:  
            # Display customer level detailes 

            with st.expander('Show/Hide MRR by Customer', expanded = True):
                st.subheader('MRR by Customer :', divider='green') 
 
                display_replan_customer_arr_df = st.session_state.replan_customer_arr_df.round(2)

                # set inde to customerName  - for freeze pane functionality
                display_replan_customer_arr_df.set_index(['customerName'], inplace=True)
                st.dataframe(display_replan_customer_arr_df, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            # Display customer count level detailes 
            with st.expander('Show/Hide Customer Count', expanded = True):
                st.subheader('Customer Count :', divider='green') 

                display_replan_logo_metrics_df = rename_columns(st.session_state.replan_logo_metrics_df.round(0))
                display_replan_logo_metrics_df.set_index(['measureType'], inplace=True)

                display_replan_logo_metrics_df = decorate_logo_metrics_df(display_replan_logo_metrics_df)
                st.dataframe(display_replan_logo_metrics_df, use_container_width=True)

            st.subheader('ARR Walk (by Type) :', divider='green') 

            # set inde to customerId, measureType - for freeze pane functionality
            display_replan_metrics_df = stylize_metrics_df(st.session_state.replan_metrics_df)
            st.dataframe(display_replan_metrics_df, use_container_width=True)


    # -- Create sidebar for plot controls
    # st.sidebar.title('AI helper')
    # query= st.sidebar.text_area('Ask your question - not implemented yet')
    # st.sidebar.button(label="Ask - @todo")

if __name__ == "__main__":
    main()


