import streamlit as st
import pandas as pd
import os
import base64

# Function to create a download link for CSV file
def get_csv_download_link(dataframe):
    csv_file = dataframe.to_csv(index=False)
    b64 = base64.b64encode(csv_file.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="dataframe.csv">Download CSV File</a>'
    return href

# Function to list filenames in the 'data' folder
def list_files_in_data_folder():
    data_folder = 'data'
    return os.listdir(data_folder)

# Main Streamlit app
def main():
    st.title("DataFrame Save and Load App")

    # Initialize the DataFrame with sample data
    data = {'Column1': [1, 2, 3],
            'Column2': ['A', 'B', 'C']}
    df = pd.DataFrame(data)

    # Display the DataFrame
    st.write("Current DataFrame:")
    st.write(df)

    # Define the data folder as 'data'
    data_folder = 'data'

    # Create the 'data' subfolder if it doesn't exist
    os.makedirs(data_folder, exist_ok=True)

    # Button to save the DataFrame to a CSV file in the 'data' subfolder
    if st.button("Save DataFrame to CSV"):
        file_path = os.path.join(data_folder, 'dataframe.csv')
        df.to_csv(file_path, index=False)
        st.success(f"DataFrame saved to '{file_path}'")

    # Button to load the DataFrame from a CSV file
    if st.button("Load DataFrame from CSV"):
        file_list = list_files_in_data_folder()
        if 'dataframe.csv' in file_list:
            file_path = os.path.join(data_folder, 'dataframe.csv')
            try:
                df = pd.read_csv(file_path)
                st.success(f"DataFrame loaded successfully from '{file_path}'")
            except FileNotFoundError:
                st.error(f"File '{file_path}' not found. Please save the DataFrame first.")
        else:
            st.warning("No saved CSV file found in the 'data' folder. Please save the DataFrame first.")

    # Display the filenames of all files in the 'data' folder
    st.write("Filenames in 'data' folder:")
    file_list = list_files_in_data_folder()
    for filename in file_list:
        st.write(filename)

    # Display the updated DataFrame
    st.write("Updated DataFrame:")
    st.write(df)

    # Provide a link to download the DataFrame as a CSV
    st.markdown(get_csv_download_link(df), unsafe_allow_html=True)

if __name__ == '__main__':
    main()
