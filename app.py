import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from dotenv import load_dotenv
import os

#================================== Database Connection ==================================#

# Load .env file
load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("POSTGRES_DB"), 
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT")
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

try:
    query_sample_incident_reports = 'SELECT * FROM incident_reports LIMIT 20'
    df_sample_incident_reports = pd.read_sql(query_sample_incident_reports,conn)
    st.caption('20 Sample Rows from incident_reports Table')
    st.dataframe(df_sample_incident_reports, use_container_width=True)

    query_sample_citizens = 'SELECT * FROM citizens LIMIT 20'
    df_sample_citizens = pd.read_sql(query_sample_citizens,conn)
    st.caption('20 Sample Rows from citizens Table')
    st.dataframe(df_sample_citizens, use_container_width=True)

    query_sample_incident_details = 'SELECT * FROM incident_details LIMIT 20'
    df_sample_incident_details = pd.read_sql(query_sample_incident_details,conn)
    st.caption('20 Sample Rows from incident_details Table')
    st.dataframe(df_sample_incident_details, use_container_width=True)

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

#=========================== Highest Show of Force Bar Chart ===============================#
st.markdown('---')
st.subheader('Distribution of Highest Show of Force')
query_show_force = "SELECT highest_show_of_force FROM incident_reports"
try:
    df_show_force = pd.read_sql(query_show_force, conn)
    force_counts = (df_show_force['highest_show_of_force'].fillna('Unknown').str.strip().value_counts().reset_index())
    force_counts.columns = ['Highest Show of Force', 'Count']

    figure_force = px.bar(force_counts, x='Highest Show of Force', y='Count', text='Count', color='Highest Show of Force', color_discrete_sequence = px.colors.qualitative.Set2)
    figure_force.update_traces(textposition = 'outside')
    figure_force.update_layout(xaxis_title = 'Show of Force Type', yaxis_title = 'Number of Incidents', showlegend = False, xaxis_tickangle = -30)
    st.plotly_chart(figure_force, use_container_width = True)
except Exception as e:
    st.error(f"Error loading show of force charts: {e}")

