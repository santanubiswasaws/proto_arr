import pandas as pd
import streamlit as st


#from langchain.llms import OpenAI
from openai import OpenAI 
from dotenv import load_dotenv
import os

from fuzzywuzzy import process


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



def extract_customer_name_with_gpt3(query):
    # Few-shot prompt with examples
    prompt = """
    Extract the customer or company name from the following sentences:

    Sentence: "What is the total revenue from Company A"
    Customer Name: "Company A"

    Sentence: "What is the total revenue from company A"
    Customer Name: "company A"

    Sentence: "What is the total revenue from Company B in 2023"
    Customer Name: "Company B"

    Sentence: "What is the rate of increase in MRR from Johnson & Johnson"
    Customer Name: "Johnson & Johnson"

    Sentence: "When did Information Technology Institute churn?"
    Customer Name: "Information Technology Institute"

    Sentence: "When did information Technology Institute churn?"
    Customer Name: "information Technology Institute"

    Sentence: "What is the revenue growth rate from visa Inc. in 2023?"
    Customer Name: "visa Inc."

    Sentence: "What was the revenue growth from A9 Technologies in 2024?"
    Customer Name: "A9 Technologies"
"""

    full_prompt = prompt + f"\Sentence: \"{query}\"\nCustomer Name::"

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo-0613", messages=[{"role": "system", "content": full_prompt}])
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
customer_query  = input("Enter customer related question : ") 
extracted_name = extract_customer_name_with_gpt3(customer_query)
print(f"Extracted Name: {extracted_name}")


agg_file_path = 'data/pvt_metrics_df.csv'
agg_df = pd.read_csv(agg_file_path)

cust_file_path = 'data/pvt_cust_df.csv'
cust_df = pd.read_csv(cust_file_path)

# Assuming df is your DataFrame
# Replace 'customerName' and 'customerId' with your actual column names

# Remove duplicates based on customerName and customerId
unique_customers_df = cust_df[['customerName', 'customerId']].drop_duplicates()

# Convert to dictionary if needed
unique_customers_dict = unique_customers_df.set_index('customerName').to_dict()['customerId']


def fuzzy_match_customer(name_to_match, customers_dict):
    if name_to_match:
        # Get a list of customer names for fuzzy matching
        customer_names = list(customers_dict.keys())
        
        # Use fuzzy matching to find the closest customer name
        best_match, score = process.extractOne(name_to_match, customer_names)
        
        # Retrieve the customer ID for the best match
        best_match_id = customers_dict.get(best_match)
        
        return best_match, best_match_id, score  # Returns the best match, its ID, and the similarity score
    else:
        return None, None, 0  # No name to match
    

best_match, best_match_id, match_score = fuzzy_match_customer(extracted_name, unique_customers_dict)
print(f"Extracted Name: {extracted_name}")
print(f"Best Fuzzy Match: {best_match} with ID: {best_match_id} and Score: {match_score}")


def crate_df_agent(df, model):

    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model=model),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )
    return agent
wh
agg_agent = crate_df_agent(agg_df, llm_model)

cust_agent = crate_df_agent(cust_df, llm_model)

user_query = input("Please enter some text for agg: ") 
response = agg_agent.run(user_query)


user_query = input("Please enter some text for cust: ") 
response = cust_agent.run(user_query)

print(response)
