import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import plotly.express as px
from dotenv import load_dotenv
import os

#================================== Database Connection ==================================#

load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT")
}

@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        conn.autocommit = True
        return conn
    except Exception as e:
        st.error(f"Error Connecting to Database: {e}")
        return None

conn = get_db_connection()

#==================================== Title and Intro ====================================#

st.title('Phoenix Show of Force Dataset Dashboard')
st.markdown('DAEN 328 Final Project by Elias Ortiz, Bobby Cuellar, Brody Mitchell, and Jay Yan')

if st.button('Refresh Data'):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

#==================================== Sidebar Filters ====================================#

st.sidebar.header("Filter Options")

if conn is not None:
    try:
        race_query = """
            SELECT DISTINCT race
            FROM citizens
            WHERE race IS NOT NULL
            ORDER BY race
        """
        race_options = pd.read_sql(race_query, conn)['race'].tolist()
        race_options = ['All'] + race_options

        charge_query = """
            SELECT DISTINCT citizen_charge
            FROM incident_details
            WHERE citizen_charge IS NOT NULL
            ORDER BY citizen_charge
        """
        charge_options = pd.read_sql(charge_query, conn)['citizen_charge'].tolist()
        charge_options = ['All'] + charge_options

        force_query = """
            SELECT DISTINCT highest_show_of_force
            FROM incident_reports
            WHERE highest_show_of_force IS NOT NULL
            ORDER BY highest_show_of_force
        """
        force_options = pd.read_sql(force_query, conn)['highest_show_of_force'].tolist()
        force_options = ['All'] + force_options

        age_bounds_query = """
            SELECT MIN(age) AS min_age, MAX(age) AS max_age
            FROM citizens
            WHERE age IS NOT NULL
        """
        age_bounds = pd.read_sql(age_bounds_query, conn).iloc[0]
        min_age = int(age_bounds['min_age']) if pd.notna(age_bounds['min_age']) else 0
        max_age = int(age_bounds['max_age']) if pd.notna(age_bounds['max_age']) else 100

    except Exception as e:
        st.sidebar.error(f"Error loading sidebar filters: {e}")
        race_options = ['All']
        charge_options = ['All']
        force_options = ['All']
        min_age = 0
        max_age = 100
else:
    race_options = ['All']
    charge_options = ['All']
    force_options = ['All']
    min_age = 0
    max_age = 100

selected_race = st.sidebar.selectbox("Select Race", race_options)
selected_charge = st.sidebar.selectbox("Select Citizen Charge", charge_options)
selected_force = st.sidebar.selectbox("Select Highest Show of Force", force_options)

selected_age_range = st.sidebar.slider(
    "Select Age Range",
    min_value=min_age,
    max_value=max_age,
    value=(min_age, max_age)
)

sample_limit = st.sidebar.slider("Sample Row Limit", min_value=5, max_value=50, value=20, step=5)

#================================ Helper for Shared Filters ===============================#

def build_shared_filters():
    conditions = []
    params = []

    if selected_race != 'All':
        conditions.append("c.race = %s")
        params.append(selected_race)

    if selected_charge != 'All':
        conditions.append("d.citizen_charge = %s")
        params.append(selected_charge)

    if selected_force != 'All':
        conditions.append("r.highest_show_of_force = %s")
        params.append(selected_force)

    conditions.append("c.age BETWEEN %s AND %s")
    params.append(selected_age_range[0])
    params.append(selected_age_range[1])

    where_clause = ""
    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)

    return where_clause, params

#=================================== Sample Data Table ===================================#

st.markdown("---")
st.subheader('Data Sample')

try:
    shared_where, shared_params = build_shared_filters()

    query_sample_incident_reports = f"""
        SELECT DISTINCT r.*
        FROM incident_reports r
        LEFT JOIN incident_details d
            ON r.incident_report_num = d.incident_report_num
        LEFT JOIN citizens c
            ON d.citizen_num = c.citizen_num
        {shared_where}
        LIMIT {sample_limit}
    """
    df_sample_incident_reports = pd.read_sql(
        query_sample_incident_reports, conn, params=shared_params
    )
    st.caption(f'{sample_limit} Sample Rows from incident_reports Table')
    st.dataframe(df_sample_incident_reports, use_container_width=True)

    query_sample_citizens = f"""
        SELECT DISTINCT c.*
        FROM citizens c
        LEFT JOIN incident_details d
            ON c.citizen_num = d.citizen_num
        LEFT JOIN incident_reports r
            ON d.incident_report_num = r.incident_report_num
        {shared_where}
        LIMIT {sample_limit}
    """
    df_sample_citizens = pd.read_sql(
        query_sample_citizens, conn, params=shared_params
    )
    st.caption(f'{sample_limit} Sample Rows from citizens Table')
    st.dataframe(df_sample_citizens, use_container_width=True)

    query_sample_incident_details = f"""
        SELECT DISTINCT d.*
        FROM incident_details d
        LEFT JOIN citizens c
            ON d.citizen_num = c.citizen_num
        LEFT JOIN incident_reports r
            ON d.incident_report_num = r.incident_report_num
        {shared_where}
        LIMIT {sample_limit}
    """
    df_sample_incident_details = pd.read_sql(
        query_sample_incident_details, conn, params=shared_params
    )
    st.caption(f'{sample_limit} Sample Rows from incident_details Table')
    st.dataframe(df_sample_incident_details, use_container_width=True)

except Exception as e:
    st.error(f"Error loading sample data: {e}")

#=============================== Charge By Race Bar Charts ===============================#

st.markdown("---")
st.subheader('Distribution of Charge by Race')

query_charge_race = f"""
    SELECT c.race, d.citizen_charge
    FROM incident_details d
    JOIN citizens c
        ON d.citizen_num = c.citizen_num
    JOIN incident_reports r
        ON d.incident_report_num = r.incident_report_num
    {shared_where}
"""

try:
    df_charge_race = pd.read_sql(query_charge_race, conn, params=shared_params)

    if df_charge_race.empty:
        st.warning("No data available for the selected filters.")
    else:
        for race in df_charge_race['race'].dropna().unique():
            df_race = df_charge_race[df_charge_race['race'] == race]
            counts = df_race['citizen_charge'].value_counts()

            fig, ax = plt.subplots()
            ax.bar(counts.index, counts.values)
            plt.xticks(rotation=45, ha='right')
            ax.set_title(f"{race}")
            ax.set_xlabel("Citizen Charge")
            ax.set_ylabel("Count")
            st.pyplot(fig)

except Exception as e:
    st.error(f"Error creating charge by race charts: {e}")

#=========================== Highest Show of Force Bar Chart ==============================#

st.markdown('---')
st.subheader('Distribution of Highest Show of Force')

query_show_force = f"""
    SELECT r.highest_show_of_force
    FROM incident_reports r
    LEFT JOIN incident_details d
        ON r.incident_report_num = d.incident_report_num
    LEFT JOIN citizens c
        ON d.citizen_num = c.citizen_num
    {shared_where}
"""

try:
    df_show_force = pd.read_sql(query_show_force, conn, params=shared_params)

    if df_show_force.empty:
        st.warning("No show of force data available for the selected filters.")
    else:
        force_counts = (
            df_show_force['highest_show_of_force']
            .fillna('Unknown')
            .astype(str)
            .str.strip()
            .value_counts()
            .reset_index()
        )
        force_counts.columns = ['Highest Show of Force', 'Count']

        figure_force = px.bar(
            force_counts,
            x='Highest Show of Force',
            y='Count',
            text='Count',
            color='Highest Show of Force'
        )
        figure_force.update_traces(textposition='outside')
        figure_force.update_layout(
            xaxis_title='Show of Force Type',
            yaxis_title='Number of Incidents',
            showlegend=False,
            xaxis_tickangle=-30
        )
        st.plotly_chart(figure_force, use_container_width=True)

except Exception as e:
    st.error(f"Error loading show of force charts: {e}")