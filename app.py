import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

#================================== Database Connection ==================================#

DB_PARAMS = {
    "dbname": "ProjectDB", 
    "user": "postgres",
    "password": "oakmont2016",
    "host": "localhost",
    "port": "5432"
}

# Helper function to create connection
@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("Database Connection Successful\n")
        return conn
    except Exception as e:
        print(f'Error Connecting to Database: {e}')

# Create connection
conn = get_db_connection()

#==================================== Title and Intro ====================================#

st.title('Phoenix Show of Force Dataset Dashboard')
st.markdown('DAEN 328 Final Project by Elias Ortiz, Bobby Cuellar, Brody Mitchell, and Jay Yan')

# Refresh button
if st.button('Refresh Data'):
    st.rerun()

#=================================== Sample Data Table ===================================#

st.markdown("---")

st.subheader('Data Sample')

query_sample = 'SELECT * FROM incident_reports LIMIT 20'

try:
    df_sample = pd.read_sql(query_sample,conn)

    st.dataframe(df_sample, use_container_width=True)
    st.caption('20 Sample Rows from incident_reports')
except Exception as e:
    st.error(f"Error loading sample data: {e}")

#=============================== Charge By Race Pie Charts ===============================#

st.markdown("---")

st.subheader('Distribution of Charge by Race')

query_pie = "SELECT race, citizen_charge FROM incident_details JOIN citizens ON incident_details.citizen_num=citizens.citizen_num"

try:
    # Get a dataframe containing just the citizen's race and charge
    df_pie = pd.read_sql(query_pie,conn)

    # Loop through all races
    for race in df_pie['race'].unique():
        # If a race is not null
        if race:
            # Get only rows of that race
            df_pie_race = df_pie[df_pie['race'].notna() & df_pie['race'].str.contains(race)]
            # Get the counts of each charge
            counts = df_pie_race['citizen_charge'].value_counts()

            # Create a bar plot showing the number of different charge types for that race
            fig, ax = plt.subplots()
            ax.bar(counts.index, counts.values)
            plt.xticks(rotation=45,ha='right')
            ax.set_title(race)
            st.pyplot(fig)
except Exception as e:
    st.error(f"Error creating pie charts: {e}")


