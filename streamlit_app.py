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

    # Read each valid JSON file and collect the relevant data
    for json_file in json_files:
        file_name = json_file.split('.')[0]
        file_path = os.path.join(alerts_folder_path, json_file)
        with open(file_path, 'r') as f:
            records = json.load(f)
            for record in records:
                subtype = record.get('subtype', 'message')
                if not subtype:
                    subtype = 'message'
                display_name = record.get('user_profile', {}).get('display_name', 'Unknown')
                text = record.get('text', '')
                if text == '':
                    continue
                ts = record.get('ts', '')
                if ts:
                    timestamp = datetime.fromtimestamp(float(ts))
                    date = timestamp.strftime('%Y-%m-%d')
                    day_of_week = timestamp.strftime('%A')
                    time = timestamp.strftime('%H:%M:%S')
                    hour = timestamp.strftime('%H')
                else:
                    date = ''
                    day_of_week = ''
                    time = ''
                    hour = ''
                data.append({
                    'file_name': file_name, 
                    'subtype': subtype, 
                    'display_name': display_name, 
                    'text': text, 
                    'date': date, 
                    'day_of_week': day_of_week, 
                    'time': time,
                    'hour': hour
                })

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

    # Create a heatmap of file_name and display_name
    heatmap_df = filtered_df.groupby(['file_name', 'display_name']).size().reset_index(name='count')
    fig_heatmap = px.density_heatmap(heatmap_df, x='file_name', y='display_name', z='count', 
                                     title='Heatmap of Mentions by File and Display Name',
                                     labels={'file_name': 'File Name', 'display_name': 'Display Name', 'count': 'Count'},
                                     hover_data={'file_name': True, 'display_name': True, 'count': True})
    fig_heatmap.update_layout(xaxis=dict(tickmode='linear', tickvals=heatmap_df['file_name'].unique()))

    st.plotly_chart(fig_heatmap)

    # Filter data for bot_message subtype
    bot_message_df = df[df['subtype'] == 'bot_message']

    # Create a table for the text field where subtype="bot_message"
    if not bot_message_df.empty:
        text_count_df = bot_message_df['text'].value_counts().reset_index()
        text_count_df.columns = ['text', 'count']
        merged_df = pd.merge(bot_message_df, text_count_df, on='text')
        bot_message_table = merged_df[['text', 'count', 'date', 'day_of_week', 'time']].drop_duplicates()
        st.write("Bot Messages Text Count with Date and Time")
        st.dataframe(bot_message_table)

        # Create a chart for count of day_of_week and time (grouped into hour of the day) using bot_message_table
        if not bot_message_table.empty:
            day_hour_df = bot_message_table.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
            fig_day_hour = px.bar(day_hour_df, x='hour', y='count', color='day_of_week', barmode='group',
                                  title='Count of Bot Messages by Day of Week and Hour of the Day',
                                  labels={'hour': 'Hour of the Day', 'count': 'Count', 'day_of_week': 'Day of Week'})
            st.plotly_chart(fig_day_hour)
