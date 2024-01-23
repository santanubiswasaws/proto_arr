# utilities for helping AI 

llm_model="gpt-3.5-turbo-0613"

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

Question: "what is the total revenue for Customer A in Q2 of 2023?"
Answer: customer_arr_df

Question: "what is the total revenue for Customer B in July of 2021?"
Answer: customer_arr_df

Question: "what is the total churn for Customer C in July of 2021?"
Answer: customer_arr_df

Question: "what is the total churn for Customer D in Q4 of 2025?"
Answer: customer_arr_df

"""