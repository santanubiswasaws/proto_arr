import streamlit as st
import pandas as pd
import altair as alt

from arr_lib.styling import BUTTON_STYLE
from arr_lib.styling import MARKDOWN_STYLES
from arr_lib.styling import GLOBAL_STYLING



def arr_walk_chart(metrics_df, bar_color, chart_title): 
    """
    generate and return an altair chart - for customer ARR walk 
    """
    # Check if 'Total_Sales' column exists, and drop it if it does
    if 'Total_Sales' in metrics_df.columns:
        metrics_df = metrics_df.drop(columns=['Total_Sales'])

    # Running ARR charts 
    melted_metrics_df = pd.melt(metrics_df, id_vars=['measureType'], var_name='month', value_name='ARR')

    arr_df = melted_metrics_df[melted_metrics_df['measureType']=='monthlyRevenue']
    # Convert 'month' to datetime and extract year and quarter
    arr_df['month'] = pd.to_datetime(arr_df['month'])
    arr_df['quarter'] = arr_df['month'].dt.year.astype(str) + '-Q' + arr_df['month'].dt.quarter.astype(str)

    # Group by quarter and sum/average the ARR
    #quarterly_data = arr_df.groupby('quarter')['ARR'].mean().reset_index()


    # Filter to keep only the third month of each quarter
    third_months = arr_df[arr_df['month'].dt.month.isin([3, 6, 9, 12])]

    # Group by quarter and take the value of the third month
    quarterly_data = third_months.groupby('quarter')['ARR'].last().reset_index()



    # Transform and scale the ARR values to thousands for the bar chart
    bar_chart = alt.Chart(quarterly_data).transform_calculate(
        scaled_arr="datum.ARR / 1000"  # Scaling the ARR to thousands
    ).mark_bar(color=bar_color).encode(
        x=alt.X('quarter', title=None),
        y=alt.Y('scaled_arr:Q', title="Quarterly ARR (in Thousands) ", axis=alt.Axis(format=',.0f')) 
    )

    # Create the text layer for labels, using the same scaled values
    text_chart = bar_chart.mark_text(
        align='left',
        baseline='middle',
        angle=270,  # Rotate the text by 270 degrees
        dx=3,  # Horizontal offset
        dy=-5,  # Vertical offset
        fontSize=12,
        color='gray'
    ).encode(
        x='quarter',
        y='scaled_arr:Q',  # Use scaled ARR for positioning text
        text=alt.Text('scaled_arr:Q', format=',.0f')  # Display scaled ARR
    )

    # Layer the text and the bar chart
    arr_walk_chart = alt.layer(bar_chart, text_chart).properties(
        title=chart_title,
        width=800,
        height=400
    ).configure_title(
        fontSize=14,
        fontWeight='normal', 
        anchor='middle',
        orient='bottom', 
        color='gray'
    ).configure_axis(
        gridColor='#efefef'  # Set grid line color
    )    

    return arr_walk_chart




def cust_count_chart(df, chart_color, chart_title): 
       
    # Check if 'Total_Sales' column exists, and drop it if it does
    if 'Total_Sales' in df.columns:
        df = df.drop(columns=['Total_Sales'])

        # Running Customer Count 
    melted_count_df = pd.melt(df, id_vars=['measureType'], var_name='month', value_name='customerCount')

    count_df = melted_count_df[melted_count_df['measureType']=='monthlyRevenueLogo']

    # Transform and scale the ARR values to thousands for the bar chart
    cust_count_result = alt.Chart(count_df).mark_bar(color=chart_color).encode(
        x=alt.X('month', title=None),
        y=alt.Y('customerCount:Q', title="Monthly Count ", axis=alt.Axis(format=',.0f')) 
    ).properties(
        title=chart_title,
        width=800,
        height=350
    ).configure_title(
        fontSize=14,
        fontWeight='normal',
        anchor='middle',
        orient='bottom', 
        color='gray'
    ).configure_axis(
        gridColor='#efefef'  # Set grid line color
    )

    return cust_count_result


def cust_count_waterfall_chart(df,  chart_title): 

     
    # Check if 'Total_Sales' column exists, and drop it if it does
    if 'Total_Sales' in df.columns:
        df = df.drop(columns=['Total_Sales'])
 
    # Running Customer Count 
    melted_count_df = pd.melt(df, id_vars=['measureType'], var_name='month', value_name='customerCount')

    # Calculate min and max values with a bit of padding
    min_count = melted_count_df['customerCount'].min() - (melted_count_df['customerCount'].max() - melted_count_df['customerCount'].min()) * 0.1
    max_count = melted_count_df['customerCount'].max() + (melted_count_df['customerCount'].max() - melted_count_df['customerCount'].min()) * 0.1


    # Assuming df is your DataFrame with columns 'month', 'measureType', and 'customerCount'

    # Define a dictionary for translating category names
    translate_dict = {
        'churnLogo': 'Churn',
        'newBusinessLogo': 'New Logo',
        'lastMonthRevenueLogo': 'Previous Count',
        'monthlyRevenueLogo': 'Monthly Count'
    }

    # Define the color scheme as a dictionary
    color_scheme = {
        'Churn': '#ee7777',
        'New Logo': '#77aaca',
        'Previous Count': 'lightgray',
        'Monthly Count': '#88b988'
    }

    # Apply the translation to the DataFrame
    melted_count_df['translated_measureType'] = melted_count_df['measureType'].map(translate_dict)

    # Create a line chart
    count_wf_chart = alt.Chart(melted_count_df).mark_line(point=True).encode(
        x=alt.X('month:T', axis=alt.Axis(title=None, labelAngle=270, labelOverlap=True)),  # Assuming 'month' is of datetime type; if not, change to 'month:N'
        y=alt.Y('customerCount:Q', axis=alt.Axis(title='Customer Count', format=',.0f'), scale=alt.Scale(domain=(min_count, max_count))),
        color=alt.Color('translated_measureType:N', scale=alt.Scale(domain=list(color_scheme.keys()), range=list(color_scheme.values())), legend=alt.Legend(title=None, orient='top')),  # Position legend at top
        tooltip=['month', 'translated_measureType', 'customerCount']
    ).properties(
        title=chart_title,
        width=800,
        height=350
    ).configure_title(
        fontSize=14,
        fontWeight='normal',
        anchor='middle',
        orient='bottom', 
        color='gray')
    
    return count_wf_chart


def top_cust_chart(customer_arr_df, bar_color, chart_title): 
    """
    generate and return an altair chart - for customer pareto 
    """

    # Check if 'Total_Sales' column exists, and drop it if it does
    if 'Total_Sales' in customer_arr_df.columns:
        customer_arr_df = customer_arr_df.drop(columns=['Total_Sales'])

    # Create a new column with the sum of monthly sales
    customer_arr_df['Total_Sales'] = customer_arr_df.iloc[:, 2:].sum(axis=1)

    # Sort the DataFrame by 'Total_Sales' in descending order
    customer_arr_df = customer_arr_df.sort_values(by='Total_Sales', ascending=False)

    # Optionally, reset the index if you want the index to be sequential
    top_10_customers = customer_arr_df.head(10)
    top_10_customers = top_10_customers [['customerName', 'Total_Sales']]


    top_bar_chart = alt.Chart(top_10_customers).transform_calculate(
        scaled_tcv="datum.Total_Sales / 1000"  # Scaling the ARR to thousands
    ).mark_bar(color=bar_color).encode(
        x=alt.X('customerName', title=None, sort=None),
        y=alt.Y('scaled_tcv:Q', title="Total Contract Values (in Thousands)", axis=alt.Axis(format=',.0f'))
    )

        # Create the text layer for labels, with text rotated by 270 degrees
    top_text_chart = top_bar_chart.mark_text(
        align='left',
        baseline='middle',
        angle=270,  # Rotate the text by 270 degrees
        dx=5,  # Adjust this value to position the text correctly with respect to the bar
        dy=-3,  # Adjust this value to position the text correctly on the bar
        fontSize=12,
        color='gray'
    ).encode(
        y='scaled_tcv:Q',  # Use scaled ARR for positioning text
        text=alt.Text('scaled_tcv:Q', format=',.0f')  # Display scaled TCV
    )

    # Layer the text and the bar chart
    top_final_chart = alt.layer(top_bar_chart, top_text_chart).properties(
        title=chart_title,
        width=800,
        height=500
    ).configure_title(
        fontSize=14,
        fontWeight='normal', 
        anchor='middle',
        orient='bottom', 
        color='gray'
    ).configure_axis(
        gridColor='#efefef'  # Set grid line color
    )    

    return top_final_chart