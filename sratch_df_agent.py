import pandas as pd
import streamlit as st


#from langchain.llms import OpenAI
from openai import OpenAI 
from dotenv import load_dotenv
import os


from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

llm_model="gpt-3.5-turbo-0613"

load_dotenv()

# Load the OpenAI API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None or api_key == "":
    print("OPENAI_API_KEY is not set")
    exit(1)
else:
    print("OPENAI_API_KEY is set")

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)




agg_file_path = 'data/pvt_metrics_df.csv'
agg_df = pd.read_csv(agg_file_path)



print (agg_df['year'].dtype)

cust_file_path = 'data/pvt_cust_df.csv'
cust_df = pd.read_csv(cust_file_path)

print (cust_df['year'].dtype)

def crate_df_agent(df, model):

    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model=model),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )
    return agent

agg_agent = crate_df_agent(agg_df, llm_model)

cust_agent = crate_df_agent(cust_df, llm_model)

user_query = input("Please enter some text for agg: ") 
response = agg_agent.run(user_query)


user_query = input("Please enter some text for cust: ") 
response = cust_agent.run(user_query)

print(response)
