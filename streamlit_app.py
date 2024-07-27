import streamlit as st
import zipfile
import os
import json
import pandas as pd
import plotly.express as px
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

    # Read each valid JSON file and collect the number of records and subtypes
    for json_file in json_files:
        file_name = json_file.split('.')[0]
        file_path = os.path.join(alerts_folder_path, json_file)
        with open(file_path, 'r') as f:
            records = json.load(f)
            for record in records:
                subtype = record.get('subtype', 'Unknown')
                data.append({'file_name': file_name, 'subtype': subtype})

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)
    df = df.sort_values('file_name')
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

    # Get unique subtypes
    subtypes = df['subtype'].unique()
    selected_subtypes = st.multiselect("Select subtypes to filter", subtypes, default=subtypes)

    # Filter data based on selected subtypes
    filtered_df = df[df['subtype'].isin(selected_subtypes)]

    # Create an interactive bar chart
    bar_df = filtered_df.groupby('file_name').size().reset_index(name='record_count')
    fig_bar = px.bar(bar_df, x='file_name', y='record_count', title='Number of Alert Records per File', 
                     labels={'file_name': 'File Name', 'record_count': 'Number of Records'},
                     hover_data={'file_name': True, 'record_count': True})
    fig_bar.update_layout(xaxis=dict(tickmode='linear'))

    st.plotly_chart(fig_bar)

    # Create a heatmap of file_name and subtype
    heatmap_df = filtered_df.groupby(['file_name', 'subtype']).size().reset_index(name='count')
    fig_heatmap = px.density_heatmap(heatmap_df, x='file_name', y='subtype', z='count', 
                                     title='Heatmap of Alert Records by File and Subtype',
                                     labels={'file_name': 'File Name', 'subtype': 'Subtype', 'count': 'Count'},
                                     hover_data={'file_name': True, 'subtype': True, 'count': True})
    fig_heatmap.update_layout(xaxis=dict(tickmode='linear'))

    st.plotly_chart(fig_heatmap)
