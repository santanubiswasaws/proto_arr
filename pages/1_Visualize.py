import streamlit as st
import pandas as pd
import altair as alt


print('...........in visualize..............')
print (st.session_state.uploaded_file) 

metrics_df = st.session_state.metrics_df
customer_arr_df = st.session_state.customer_arr_df
if metrics_df.empty: 
    st.error('Please generate ARR metrics')
else:

    # Running ARR charts 
    melted_metrics_df = pd.melt(metrics_df, id_vars=['measureType'], var_name='month', value_name='ARR')
    st.subheader('ARR Trends', divider='green')
    st.line_chart(melted_metrics_df[melted_metrics_df['measureType']=='Opening Period ARR'], x="month", y="ARR")
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Top 10 customers - with highest lifetime value 

    # Create a new column with the sum of monthly sales
    customer_arr_df['Total_Sales'] = customer_arr_df.iloc[:, 2:].sum(axis=1)

    # Sort the DataFrame by 'Total_Sales' in descending order
    customer_arr_df = customer_arr_df.sort_values(by='Total_Sales', ascending=False)

    # Optionally, reset the index if you want the index to be sequential
    customer_arr_df = customer_arr_df.reset_index(drop=True)
    top_10_customers = customer_arr_df.head(10)

    top_10_customers = top_10_customers [['customerName', 'Total_Sales']]

    st.subheader('Customer revenue details ', divider='green')

    col1, col2 = st.columns(2)
    with col1: 
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.write(alt.Chart(top_10_customers, title="Top Customers with lifetime value").mark_bar(size=20).encode(
            x=alt.X('customerName', sort=None),
            y='Total_Sales',
        ).configure_axis(
                grid=False
            ).configure_view(
                stroke=None
            ).properties(width=400, height=400))
    with col2: 
        # Print the sorted DataFrame
        st.dataframe(top_10_customers.round(0), use_container_width=True,  hide_index=True)

print('........... end of  visualize..............')