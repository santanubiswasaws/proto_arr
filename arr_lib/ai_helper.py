from fuzzywuzzy import process
import math

# utilities for helping AI 
llm_model="gpt-3.5-turbo-0613"

few_shot_prompt = """
Question: "What was the monthly revenue for customer XYZ in February 2024?"
Answer: customer_arr_df

Question: "Show me the total new business acquired in January 2024."
Answer: metrics_df

Question: "What are the top 10 customers?"
Answer: customer_arr_df

Question: "what is the mrr for accentur in Jan of 2023?"
Answer: customer_arr_df

Question: "what is the MRR for customer A in Jan of 2023?"
Answer: customer_arr_df

Question: "what is the monthly recurring revenue for customer C in September of 2020?"
Answer: customer_arr_df

Question: "what is the recurring revenue for customer C in September of 2020?"
Answer: customer_arr_df

Question: "what is the contract value for customer C in September of 2020?"
Answer: customer_arr_df

Question: "what is the tcv for customer A in September of 2020?"
Answer: customer_arr_df


Question: "what is the tcv for account A in September of 2020?"
Answer: customer_arr_df

Question: "Which customers churned in 2023?"
Answer: customer_arr_df

Question: "Which accounts churned in 2023?"
Answer: customer_arr_df

Question: "What is the net retention rate in Q1 of 2023?"
Answer: metrics_df

Question: "List top 2 account names as of 2023-01"
Answer: customer_arr_df

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

Question: "what is the total revenue for Customer A in Q2 of 2023?"
Answer: customer_arr_df

Question: "what is the total revenue for Customer B in July of 2021?"
Answer: customer_arr_df

Question: "what is the total churn for Customer C in July of 2021?"
Answer: customer_arr_df

Question: "what is the total churn for Customer D in Q4 of 2025?"
Answer: customer_arr_df

"""

customer_name_extract_prompt = """

    Please extract the customer or company name mentioned in each sentence exactly as it appears, without changing the case to uppercase or title case. Pay close attention to preserve the original spelling and casing :

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

    Sentence: "When did information Technology iNstitute churn?"
    Customer Name: "information Technology iNstitute"

    Sentence: "What is the revenue growth rate from visa Inc. in 2023?"
    Customer Name: "visa Inc."

    Sentence: "What was the revenue growth from A9 Technologies in 2024?"
    Customer Name: "A9 Technologies"

    Sentence: "What was the revenue growth from at&T in 2024?"
    Customer Name: "at&T"

    Sentence: "What was the revenue growth from b9 technologies in 2024?"
    Customer Name: "b9 technologies"
"""

_vocab_dict = {
    'Monthly Recurring Revenue': 'revenue',
    'MRR': 'revenue',
    'mrr': 'revenue',
    "account" : "customer",
    "accounts" : "customers",
    'monthly revenue' : 'revenue',
    'monthly recurring revenue': 'revenue',
    'Customer Churn Rate': 'have non-zero churn',
    'customer churn rate': 'have non-zero churn',
    'contract value': 'revenue',
    'tcv': 'revenue'
}

def extract_customer_name(query, llm_client):

    cust_full_prompt = customer_name_extract_prompt + f"\Sentence: \"{query}\"\nCustomer Name::"

    try:
        response = llm_client.chat.completions.create(model="gpt-3.5-turbo-0613", messages=[{"role": "system", "content": cust_full_prompt}])
        ext_customer_name = response.choices[0].message.content.strip()
        print (f"The extracted customer name from - {query} - is - {ext_customer_name}")
        return ext_customer_name

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

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


def translate_vocabulary(query):
    print(f"Original Query: {query}")

    for key, value in _vocab_dict.items():
        # Replace each occurrence of the key in the query with its corresponding value
        query = query.replace(key, value)

    print(f"Translated Query: {query}") 
    return query


def preprocess_query(query, unique_customers_dict, client):
    """
    1. Replace the query with matched customer detail -either name of id 
    2. Replace other terms/words based on the vocabulary dict - e.g. MRR to revenue 
    """
    updated_query = query 
  
    # Extract customer name   
    extracted_customer_name = extract_customer_name(query, client)

    if not is_none(extracted_customer_name):
        fuzzy_matched_customer_name, fuzzy_matched_customer_id, match_score = fuzzy_match_customer(extracted_customer_name, unique_customers_dict)
        
        print(f"{fuzzy_matched_customer_name} - {fuzzy_matched_customer_id} - {match_score}")       
        # clean up strings to eliminate quotes - sometimes returned by the name extractor 

        print (f"The original query -- {query} - extracted  name: {extracted_customer_name} matched name: {fuzzy_matched_customer_name}, score:  {match_score}")

        extracted_customer_name = extracted_customer_name.replace('"', '').replace("'", "")
        fuzzy_matched_customer_name = fuzzy_matched_customer_name.replace('"', '').replace("'", "")
        fuzzy_matched_customer_id = fuzzy_matched_customer_id.replace('"', '').replace("'", "")
        if (not is_none(fuzzy_matched_customer_name)) & (match_score > 75) :
            updated_query = updated_query.replace(extracted_customer_name, fuzzy_matched_customer_name)

    # replace other phrases based on vocabulary dictionary 
    updated_query = translate_vocabulary(updated_query)

    return updated_query



def is_none(input_s): 
    """
    Checks if a string is empty or has values like None, N/A, 'None' or "N/A" - including the quotes
    """
    s = str(input_s).replace("'", "").replace('"', "")

    if s is None:
        return True
    elif isinstance(s, str) and s.lower() in ['none', 'n/a', 'na']:
        return True
    elif isinstance(s, float) and math.isnan(s):
        return True
    else:
        return False



