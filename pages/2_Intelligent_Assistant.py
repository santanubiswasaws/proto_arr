import streamlit as st
import pandas as pd
import altair as alt

#from langchain.llms import OpenAI
from openai import OpenAI 

client = OpenAI()
from dotenv import load_dotenv
import os


from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

from arr_lib.styling import BUTTON_STYLE
from arr_lib.styling import MARKDOWN_STYLES
from arr_lib.styling import GLOBAL_STYLING

import arr_lib.arr_charts as ac

st.markdown(BUTTON_STYLE, unsafe_allow_html=True)
st.markdown(MARKDOWN_STYLES, unsafe_allow_html=True)
st.markdown(GLOBAL_STYLING, unsafe_allow_html=True)

llm_model="gpt-3.5-turbo-0613"

st.header("Intelligent Assistant")
st.markdown("<br>", unsafe_allow_html=True)

load_dotenv()

# Load the OpenAI API key from the environment variable
if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
    print("OPENAI_API_KEY is not set")
    exit(1)
else:
    print("OPENAI_API_KEY is set")


if 'metrics_df' not in st.session_state: 
    metrics_df = pd.DataFrame()
else:
    # copy uploaded ARR metrics from session 
    metrics_df = st.session_state.metrics_df.copy()
    customer_arr_waterfall_df = st.session_state.customer_arr_waterfall_df.copy()   
    customer_arr_df = st.session_state.customer_arr_df.copy()
    logo_metrics_df = st.session_state.logo_metrics_df.copy()

if 'replan_metrics_df' not in st.session_state: 
    replan_metrics_df = pd.DataFrame()
else: 
    # copy adjusted ARR metrics from session 
    replan_metrics_df = st.session_state.replan_metrics_df.copy()
    replan_customer_arr_waterfall_df = st.session_state.replan_customer_arr_waterfall_df.copy()
    replan_customer_arr_df = st.session_state.replan_customer_arr_df.copy()
    replan_logo_metrics_df = st.session_state.replan_logo_metrics_df.copy()

if (metrics_df.empty or replan_metrics_df.empty): 
    st.error('Please generate ARR metrics')
    st.stop()



if 'pivoted_cust_df' not in st.session_state: 
    st.session_state.pivoted_cust_df = pd.DataFrame()

if 'pivoted_agg_df' not in st.session_state: 
    st.session_state.pivoted_agg_df = pd.DataFrame()

with st.spinner("Preparing data for the assistant"): 
    if (st.session_state.prepare_ai_data): 


        # melt the dataframe for better query results 
        melted_customer_arr_waterfall_df = customer_arr_waterfall_df.melt(id_vars=['customerId', 'customerName', 'measureType'], 
                            var_name='month', 
                            value_name='amount')

        # Splitting the 'yearMonth' into 'Year' and 'Month'
        split_columns = melted_customer_arr_waterfall_df['month'].str.split('-', expand=True)
        melted_customer_arr_waterfall_df['year'] = split_columns[0]
        melted_customer_arr_waterfall_df['monthOfYear'] = split_columns[1]
        melted_customer_arr_waterfall_df = melted_customer_arr_waterfall_df[melted_customer_arr_waterfall_df['amount'] != 0]




        # Filter the DataFrame for specific measureType values
        filtered_df = melted_customer_arr_waterfall_df[melted_customer_arr_waterfall_df['measureType'].isin(['monthlyRevenue', 'churn'])]

        filtered_df['measureType'] = filtered_df['measureType'].replace('monthlyRevenue', 'revenue')

        #Filter the DataFrame for specific measureType values
        filtered_df = filtered_df[filtered_df['measureType'].isin(['revenue', 'churn'])]

        #Using pivot_table on the filtered DataFrame
        pivoted_cust_df = filtered_df.pivot_table(index=['customerId', 'customerName', 'month', 'year', 'monthOfYear'], 
                                            columns='measureType', 
                                            values='amount',
                                            aggfunc='first').fillna(0)

        #Resetting the index to turn the indexes back into columns
        pivoted_cust_df.reset_index(inplace=True)
  
        st.session_state.pivoted_cust_df = pivoted_cust_df

        # melt the dataframe for better query results 
        melted_metrics_df = metrics_df.melt(id_vars=['measureType'], 
                            var_name='month', 
                            value_name='amount')


        # vidide the amounts with 12 - as it is annualized
        melted_metrics_df['amount'] = melted_metrics_df['amount'] / 12
        # Splitting the 'YearMonth' into 'Year' and 'Month'
        split_columns_agg = melted_metrics_df['month'].str.split('-', expand=True)
        melted_metrics_df['year'] = split_columns_agg[0]
        melted_metrics_df['monthOfYear'] = split_columns_agg[1]
        #melted_metrics_df = melted_metrics_df[melted_metrics_df['amount'] != 0]

        # Filter the DataFrame for specific measureType values
        filtered_df_1 = melted_metrics_df[melted_metrics_df['measureType'].isin(['monthlyRevenue', 'churn'])]

        filtered_df_1['measureType'] = filtered_df_1['measureType'].replace('monthlyRevenue', 'revenue')
        # Using pivot_table on the filtered DataFrame
        pivoted_agg_df = filtered_df_1.pivot_table(index=['month', 'year', 'monthOfYear'], 
                                            columns='measureType', 
                                            values='amount',
                                            aggfunc='first').fillna(0)
        # Resetting the index to turn the indexes back into columns
        pivoted_agg_df.reset_index(inplace=True)
        st.session_state.pivoted_agg_df = pivoted_agg_df

        st.session_state.prepare_ai_data = False


    pivoted_cust_df = st.session_state.pivoted_cust_df 
    pivoted_cust_df['year'] = pd.to_numeric(pivoted_cust_df['year'], errors='coerce').fillna(0).astype(int)
    pivoted_cust_df['monthOfYear'] = pd.to_numeric(pivoted_cust_df['monthOfYear'], errors='coerce').fillna(0).astype(int)  

    pivoted_agg_df = st.session_state.pivoted_agg_df 
    pivoted_agg_df['year'] = pd.to_numeric(pivoted_agg_df['year'], errors='coerce').fillna(0).astype(int)
    pivoted_agg_df['monthOfYear'] = pd.to_numeric(pivoted_agg_df['monthOfYear'], errors='coerce').fillna(0).astype(int)


def crate_df_agent(df, model):

    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model=model),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )
    return agent


# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []

# initialize flag 
if 'show_last_only' not in st.session_state:
    st.session_state['show_last_only'] = False


def classify_question(question, prompt):
    full_prompt = prompt + f"\nQuestion: \"{question}\"\nAnswer:"

    print(full_prompt)

    response = client.chat.completions.create(model="gpt-3.5-turbo-0613",
    messages=[{"role": "system", "content": full_prompt}])
    return response.choices[0].message.content.strip()

few_shot_prompt = """
Question: "What was the monthly revenue for customer XYZ in February 2024?"
Answer: customer_arr_df

Question: "Show me the total new business acquired in January 2024."
Answer: metrics_df

Question: "What are the top 10 customers?"
Answer: customer_arr_df

Question: "Which customers churned in 2023?"
Answer: customer_arr_df

Question: "What is the net retention rate in Q1 of 2023?"
Answer: metrics_df

Question: "I need details on the upsell amounts for customer ABC in the first quarter of 2024."
Answer: customer_arr_df

Question: "Which customers are up for renewal as of January 2024."
Answer: customer_arr_df

Question: "In which month does customer A churn?"
Answer: customer_arr_df

Question: "How much churn occurred across all customers in March 2024?"
Answer: metrics_df

Question: "What is the total revenue for 2024?"
Answer: metrics_df

Question: "What is the total ARR for 2024?"
Answer: metrics_df

Question: "What is the total revenue for Accenture in 2024?"
Answer: customer_arr_df

Question: "Can I get the downSell figures for customer 123 in the last six months?"
Answer: customer_arr_df

Question: "What's the overall monthly recurring revenue for the company in 2024?"
Answer: metrics_df
"""

def process_query(user_query):
    if user_query:
        # Classify the query to the appropriate dataframe
        df_to_query = classify_question(user_query, few_shot_prompt)


        response = ""
        if df_to_query == 'customer_arr_df':
            with st.spinner("FInding answer in customer metrics .."):
                cust_agent = crate_df_agent(pivoted_cust_df, llm_model)
                response = cust_agent.run(user_query)

        elif df_to_query == 'metrics_df':
            with st.spinner("FInding answer in aggregated metrics .."):
                agg_agent = crate_df_agent(pivoted_agg_df, llm_model)
                response = agg_agent.run(user_query)

        else:
            response = "Unable to process the query."

        st.session_state.show_last_only = True

        # Insert query and response at the beginning of conversation history
        st.session_state.conversation_history.insert(0, ("Response:", response))
        st.session_state.conversation_history.insert(0, ("Query:", user_query))

with st.expander("Show/Hide ustomer MRR details"): 
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(pivoted_cust_df, use_container_width=True)

with st.expander("Show/Hide aggregated ARR details"): 
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(pivoted_agg_df, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

user_query = st.text_input("Enter your query here:", key="query_input")

if st.button("Submit Query") and user_query:
    process_query(user_query)
    

# Display only the last Q&A immediately after the button is pressed
st.markdown("<br>", unsafe_allow_html=True)
if st.session_state.get('show_last_only', False):
    last_qa = st.session_state.conversation_history[:2]
    for message_type, message in last_qa:
        st.write(f"{message_type} {message}")
        if isinstance(message, pd.DataFrame):
            st.dataframe(message)
    st.session_state.show_last_only = False



# Display query history 
st.markdown(f"<br><p class='md_big'>Query History : </p>", unsafe_allow_html=True)

# Expander for chat history
with st.expander("Show/Hide Full Query History"):
    st.markdown("<br>", unsafe_allow_html=True)

    # Clear chat history button
    if st.button("Clear Chat History"):
        st.session_state.conversation_history = []
        st.experimental_rerun()
    
    for message_type, message in st.session_state.conversation_history:
        st.write(f"{message_type} {message}")
        if isinstance(message, pd.DataFrame):
            st.dataframe(message)
        # Check if the current item is an answer and not the last item in the list
        if message_type == "Response:":
            st.markdown("---")  # Horizontal line after each answer





