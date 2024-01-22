import streamlit as st
import pandas as pd
import altair as alt

from arr_lib.styling import BUTTON_STYLE
from arr_lib.styling import MARKDOWN_STYLES
from arr_lib.styling import GLOBAL_STYLING

st.markdown(BUTTON_STYLE, unsafe_allow_html=True)
st.markdown(MARKDOWN_STYLES, unsafe_allow_html=True)
st.markdown(GLOBAL_STYLING, unsafe_allow_html=True)


if 'metrics_df' not in st.session_state: 
    metrics_df = pd.DataFrame()
else:
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
        st.write(alt.Chart(top_10_customers).mark_bar(size=20).encode(
            x=alt.X('customerName', title=None, sort=None),
            y=alt.Y('Total_Sales', title="Total Sales")
        ).configure_axis(
                grid=False
            ).configure_view(
                stroke=None
            ).properties(width=400, height=400, 

                    ), theme="streamlit"

    )
        
    chart = alt.Chart(top_10_customers).mark_bar(size=22, color='#99c999').encode(
        x=alt.X('customerName', title=None, sort=None, axis=alt.Axis(domain=True, 
                    domainColor='gray', domainWidth=1, labelAngle=-45, labelLimit=500, labelOverlap=False)
                , scale=alt.Scale(padding=10)),  # Adjust padding value as needed
        y=alt.Y('Total_Sales', title="Total Sales", axis=alt.Axis(domain=False, domainColor='black', domainWidth=1))
    ).properties(
        width=420, 
        height=450,
        title='Top 10 Customers'
    ).configure_title(
        fontSize=18,
        anchor='middle',
        orient='top', 
        color='gray'
    ).configure_axis(
        labelColor='green',
        labelLimit=-10,
        grid=False
    )

    st.altair_chart(chart)




    # Assuming top_10_customers is your DataFrame

    # Create the bar chart
    bar_chart = alt.Chart(top_10_customers).mark_bar(size=22, color='#99c999').encode(
        x=alt.X('customerName', title=None, sort=None),
        y=alt.Y('Total_Sales', title="Total Sales")
    ).properties(
        width=400, 
        height=450,
        title='Top 10 Customers'
    )




        
    with col2: 
        # Print the sorted DataFrame
        st.dataframe(top_10_customers.round(0), use_container_width=True,  hide_index=True)




    # Assuming top_10_customers is a pre-defined DataFrame
    base_chart = alt.Chart(top_10_customers).mark_bar(size=20).encode(
        x=alt.X('customerName', title=None, sort=None),
        y=alt.Y('Total_Sales', title="Total Sales")
    ).properties(
        width=600, 
        height=600, title='Top 10 customers'
    ).configure_title(
        fontSize=40,
        font='Courier',
        color='gray',
        align='center',
        baseline='bottom', 
        anchor='middle', 
        orient='bottom'
    )

    st.altair_chart(base_chart)




    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)


    # Assuming top_10_customers is your DataFrame

    # Create the bar chart
    bar_chart = alt.Chart(top_10_customers).mark_bar(size=22, color='#99c999').encode(
        x=alt.X('customerName', title=None, sort=None),
        y=alt.Y('Total_Sales', title="Total Sales")
    )

    # Create the text layer for labels, with text rotated by 270 degrees
    text = bar_chart.mark_text(
        align='left',
        baseline='middle',
        angle=270,  # Rotate the text by 270 degrees
        dx=5,  # Adjust this value to position the text correctly with respect to the bar
        dy=-3  # Adjust this value to position the text correctly on the bar
    ).encode(
        text='customerName'  # Displaying 'customerName' as text on bars
    )

    # Layer the text and the bar chart
    final_chart = alt.layer(bar_chart, text).properties(
        width=400, 
        height=450,
        title='Top 10 Customers'  # Set the title here for the final chart
    )

    # Configure the final chart
    final_chart = final_chart.configure_title(
        fontSize=18,
        anchor='middle',
        orient='bottom', 
        color='gray'
    ).configure_axis(
        labelColor='green',
        labelLimit=-10,
        grid=False
    )

    st.altair_chart(final_chart)




    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)


    # Assuming top_10_customers is your DataFrame

    # Create the bar chart
    bar_chart1 = alt.Chart(top_10_customers).mark_bar(size=22, color='#99c999').encode(
        x=alt.X('customerName', title=None, sort=None,  axis=alt.Axis(labels=False)),
        y=alt.Y('Total_Sales', title="Total Sales")
    )

    # Create the text layer for labels, with text rotated by 270 degrees
    text1 = bar_chart1.mark_text(
        align='left',
        baseline='middle',
        angle=270,  # Rotate the text by 270 degrees
        dx=5,  # Adjust this value to position the text correctly with respect to the bar
        dy=-3  # Adjust this value to position the text correctly on the bar
    ).encode(
        text='customerName'  # Displaying 'customerName' as text on bars
    )

    # Layer the text and the bar chart
    final_chart1 = alt.layer(bar_chart, text1).properties(
        width=400, 
        height=450,
        title='Top 10 Customers'  # Set the title here for the final chart
    )

    # Configure the final chart
    final_chart1 = final_chart1.configure_title(
        fontSize=18,
        anchor='middle',
        orient='bottom', 
        color='gray'
    ).configure_axis(
        labelColor='green',
        labelLimit=-10,
        grid=False
    )

    st.altair_chart(final_chart1)






    ============







   


##
## Top customer waterfall analysis - by customer 
##
    
# Check if 'Total_Sales' column exists, and drop it if it does

st.subheader('Top Customers')
cust_cout_tab1, cust_cout_tab2= st.tabs(["Adjusted Values", "Uploaded Values"])

















st.subheader('ARR Trends', divider='green')
st.line_chart(melted_metrics_df[melted_metrics_df['measureType']=='monthlyRevenue'], x="month", y="ARR")
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
    st.write(alt.Chart(top_10_customers).mark_bar(size=20).encode(
        x=alt.X('customerName', title=None, sort=None),
        y=alt.Y('Total_Sales', title="Total Sales")
    ).configure_axis(
            grid=False
        ).configure_view(
            stroke=None
        ).properties(width=400, height=400, 

                ), theme="streamlit"

)
    
chart = alt.Chart(top_10_customers).mark_bar(size=22, color='#99c999').encode(
    x=alt.X('customerName', title=None, sort=None, axis=alt.Axis(domain=True, 
                domainColor='gray', domainWidth=1, labelAngle=-45, labelLimit=500, labelOverlap=False)
            , scale=alt.Scale(padding=10)),  # Adjust padding value as needed
    y=alt.Y('Total_Sales', title="Total Sales", axis=alt.Axis(domain=False, domainColor='black', domainWidth=1))
).properties(
    width=420, 
    height=450,
    title='Top 10 Customers'
).configure_title(
    fontSize=18,
    anchor='middle',
    orient='top', 
    color='gray'
).configure_axis(
    labelColor='green',
    labelLimit=-10,
    grid=False
)

st.altair_chart(chart)




# Assuming top_10_customers is your DataFrame

# Create the bar chart
bar_chart = alt.Chart(top_10_customers).mark_bar(size=22, color='#99c999').encode(
    x=alt.X('customerName', title=None, sort=None),
    y=alt.Y('Total_Sales', title="Total Sales")
).properties(
    width=400, 
    height=450,
    title='Top 10 Customers'
)




    
with col2: 
    # Print the sorted DataFrame
    st.dataframe(top_10_customers.round(0), use_container_width=True,  hide_index=True)




# Assuming top_10_customers is a pre-defined DataFrame
base_chart = alt.Chart(top_10_customers).mark_bar(size=20).encode(
    x=alt.X('customerName', title=None, sort=None),
    y=alt.Y('Total_Sales', title="Total Sales")
).properties(
    width=600, 
    height=600, title='Top 10 customers'
).configure_title(
    fontSize=40,
    font='Courier',
    color='gray',
    align='center',
    baseline='bottom', 
    anchor='middle', 
    orient='bottom'
)

st.altair_chart(base_chart)




st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)


# Assuming top_10_customers is your DataFrame

# Create the bar chart
bar_chart = alt.Chart(top_10_customers).mark_bar(size=22, color='#99c999').encode(
    x=alt.X('customerName', title=None, sort=None),
    y=alt.Y('Total_Sales', title="Total Sales")
)

# Create the text layer for labels, with text rotated by 270 degrees
text = bar_chart.mark_text(
    align='left',
    baseline='middle',
    angle=270,  # Rotate the text by 270 degrees
    dx=5,  # Adjust this value to position the text correctly with respect to the bar
    dy=-3  # Adjust this value to position the text correctly on the bar
).encode(
    text='customerName'  # Displaying 'customerName' as text on bars
)

# Layer the text and the bar chart
final_chart = alt.layer(bar_chart, text).properties(
    width=400, 
    height=450,
    title='Top 10 Customers'  # Set the title here for the final chart
)

# Configure the final chart
final_chart = final_chart.configure_title(
    fontSize=18,
    anchor='middle',
    orient='bottom', 
    color='gray'
).configure_axis(
    labelColor='green',
    labelLimit=-10,
    grid=False
)

st.altair_chart(final_chart)




st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)


# Assuming top_10_customers is your DataFrame

# Create the bar chart
bar_chart1 = alt.Chart(top_10_customers).mark_bar(size=22, color='#99c999').encode(
    x=alt.X('customerName', title=None, sort=None,  axis=alt.Axis(labels=False)),
    y=alt.Y('Total_Sales', title="Total Sales")
)

# Create the text layer for labels, with text rotated by 270 degrees
text1 = bar_chart1.mark_text(
    align='left',
    baseline='middle',
    angle=270,  # Rotate the text by 270 degrees
    dx=5,  # Adjust this value to position the text correctly with respect to the bar
    dy=-3  # Adjust this value to position the text correctly on the bar
).encode(
    text='customerName'  # Displaying 'customerName' as text on bars
)

# Layer the text and the bar chart
final_chart1 = alt.layer(bar_chart1, text1).properties(
    width=400, 
    height=450,
    title='Top 10 Customers'  # Set the title here for the final chart
)

# Configure the final chart
final_chart1 = final_chart1.configure_title(
    fontSize=18,
    anchor='middle',
    orient='bottom', 
    color='gray'
).configure_axis(
    labelColor='green',
    labelLimit=-10,
    grid=False
)

st.altair_chart(final_chart1)




# Assuming top_10_customers is your DataFrame

# Create the bar chart
bar_chart2 = alt.Chart(top_10_customers).transform_calculate(
    scaled_sales="datum.Total_Sales / 1000"  # Scaling the Total_Sales by dividing by 100,000
).mark_bar(size=22, color='#99c999').encode(
    x=alt.X('customerName:N', title=None, sort=None,  axis=alt.Axis(labels=False)),
    y=alt.Y('scaled_sales:Q', title="Total Contract Value (in Thousands)", axis=alt.Axis(format=',.0f'))  # Use scaled_sales for y-axis
)

# Create the text layer for labels, with text rotated by 270 degrees
text2 = bar_chart2.mark_text(
    align='left',
    baseline='middle',
    angle=270,  # Rotate the text by 270 degrees
    dx=5,  # Adjust this value to position the text correctly with respect to the bar
    dy=-2  # Adjust this value to position the text correctly on the bar
).encode(
    y=alt.value(330),  # Position the text at y=0, just above the x-axis
    text='customerName'  # Displaying 'customerName' as text
)

# Layer the text and the bar chart
final_chart2 = alt.layer(bar_chart2, text2).properties(
    width=400, 
    height=400,
    title='Top 10 Customers'  # Set the title here for the final chart
)

# Configure the final chart
final_chart2 = final_chart2.configure_title(
    fontSize=18,
    anchor='middle',
    orient='bottom', 
    color='gray'
).configure_axis(
    labelColor='green',
    labelLimit=-10,
    grid=False
)

st.altair_chart(final_chart2)

