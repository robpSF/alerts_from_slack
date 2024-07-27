import streamlit as st
import zipfile
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Function to load the data from the uploaded zip file
def load_data(zip_file):
    # Extract the zip file
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall("extracted_alerts")

    # Path to the alerts folder
    alerts_folder_path = os.path.join("extracted_alerts", "alerts")

    # Collect the JSON files from the alerts folder
    json_files = [f for f in os.listdir(alerts_folder_path) if f.endswith('.json')]

    # Initialize a list to store the data
    data = []

    # Read each valid JSON file and collect the number of records
    for json_file in json_files:
        try:
            date_collected = datetime.strptime(json_file.split('.')[0], '%Y-%m-%d').date()
        except ValueError:
            continue

        file_path = os.path.join(alerts_folder_path, json_file)
        with open(file_path, 'r') as f:
            records = json.load(f)
            record_count = len(records)
            data.append({'date': date_collected, 'record_count': record_count})

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    df = df.sort_values('date')
    return df

# Streamlit app
st.title("Alert Records Over Time")

# File uploader
uploaded_file = st.file_uploader("Choose a zip file", type="zip")

if uploaded_file is not None:
    # Load data
    df = load_data(uploaded_file)

    # Display the data
    st.write(df)

    # Create a bar chart
    fig, ax = plt.subplots()
    ax.bar(df['date'], df['record_count'], color='blue')
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Records")
    ax.set_title("Number of Alert Records per Date")
    plt.xticks(rotation=45)
    st.pyplot(fig)

