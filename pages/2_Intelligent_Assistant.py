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



agent_customer_arr = create_pandas_dataframe_agent(
    ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"),
    customer_arr_waterfall_df,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
)

agent_agg_arr = create_pandas_dataframe_agent(
    ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"),
    customer_arr_waterfall_df,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
)



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

Question: "How much churn occurred across all customers in March 2024?"
Answer: metrics_df

Question: "Can I get the downSell figures for customer 123 in the last six months?"
Answer: customer_arr_df

Question: "What's the overall monthly recurring revenue for the company in 2024?"
Answer: metrics_df
"""


def query_cust_dataframe(question, dataframe):
    response = agent_customer_arr.run(question)
    return response

def query_agg_dataframe(question, dataframe):
    response = agent_agg_arr.run(question)
    return response



def process_query(user_query):
    if user_query:
        # Classify the query to the appropriate dataframe
        df_to_query = classify_question(user_query, few_shot_prompt)

        # Query the designated dataframe
        response = ""
        if df_to_query == 'customer_arr_df':
            response = query_cust_dataframe(user_query, customer_arr_df)
        elif df_to_query == 'metrics_df':
            response = query_agg_dataframe(user_query, metrics_df)
        else:
            response = "Unable to classify the query."

        st.session_state.show_last_only = True

        # Insert query and response at the beginning of conversation history
        st.session_state.conversation_history.insert(0, ("Response:", response))
        st.session_state.conversation_history.insert(0, ("Query:", user_query))



# Streamlit UI setup
st.title("Intelligent Assistant")

with st.expander("Show/Hide ustomer MRR details"): 
    st.markdown("<br>", unsafe_allow_html=True)
    ai_display_customer_rr_df = customer_arr_waterfall_df.copy()
    ai_display_customer_rr_df.set_index(['customerName', 'measureType'], inplace=True)
    st.dataframe(ai_display_customer_rr_df)

with st.expander("Show/Hide aggregated ARR details"): 
    st.markdown("<br>", unsafe_allow_html=True)
    ai_display_metrics_df= metrics_df.copy()
    ai_display_metrics_df.set_index(['measureType'], inplace=True)
    st.dataframe(ai_display_metrics_df)

st.markdown("<br>", unsafe_allow_html=True)

user_query = st.text_input("Enter your query here:", key="query_input")

if st.button("Submit Query") and user_query:

    with st.spinner("FInding answer to your question .."):
        process_query(user_query)
    
    #st.session_state.query_input = ""  # Reset input box after processing

# # Display conversation history
# for message_type, message in st.session_state.conversation_history:
#     st.write(f"{message_type} {message}")
#     if isinstance(message, pd.DataFrame):
#         st.dataframe(message)  # Display dataframe directly


# Display only the last Q&A immediately after the button is pressed
st.markdown("<br>", unsafe_allow_html=True)
if st.session_state.get('show_last_only', False):
    last_qa = st.session_state.conversation_history[:2]
    for message_type, message in last_qa:
        st.write(f"{message_type} {message}")
        if isinstance(message, pd.DataFrame):
            st.dataframe(message)
    st.session_state.show_last_only = False

st.markdown("<br>", unsafe_allow_html=True)
# Expander for chat history
with st.expander("Show/Hide Full Query History"):
    st.markdown("<br>", unsafe_allow_html=True)
    for message_type, message in st.session_state.conversation_history:
        st.write(f"{message_type} {message}")
        if isinstance(message, pd.DataFrame):
            st.dataframe(message)
        # Check if the current item is an answer and not the last item in the list
        if message_type == "Response:":
            st.markdown("---")  # Horizontal line after each answer

    # Clear chat history button
    if st.button("Clear Chat History"):
        st.session_state.conversation_history = []
        st.experimental_rerun()


# if submit_button and user_query:
#     # Classify the query to the appropriate dataframe
#     df_to_query = classify_question(user_query, few_shot_prompt)

#     st.write(df_to_query)
    
#     # Query the designated dataframe
#     if df_to_query == 'customer_arr_df':
#         response = query_cust_dataframe(user_query, customer_arr_df)
#     elif df_to_query == 'metrics_df':
#         response = query_agg_dataframe(user_query, metrics_df)
#     else:
#         response = "Unable to classify the query."

#     # Display the response and the queried rows
#     st.write("Response:", response)
#     if isinstance(response, pd.DataFrame):
#         st.dataframe(response)


