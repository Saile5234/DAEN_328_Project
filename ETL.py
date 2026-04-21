import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import psycopg2
from dotenv import load_dotenv, find_dotenv
import json
import os

#=================================================== EXTRACT ===================================================#

print("#---------------- Beginning extraction -----------------#")

# How many elements in a batch
batch_size = 1000

# URL and parameters for the request
url = 'https://www.phoenixopendata.com/api/3/action/datastore_search'
params = {
    'resource_id' : '7e9d5fc7-ce02-4108-80af-369b1b54c4ff',
    'limit' : batch_size,
    'offset' : 0
}

# List for holding the data
data = []

# The size of the last batch (intitial value of 1 to ensure the loop runs)
last_batch_size = 1

# While there are still more rows to load
while last_batch_size > 0:
    # Make request
    response = requests.get(url, params=params)
    response.raise_for_status()

    # Get batch from response JSON and add it to the overall data list
    current_batch = response.json()['result']['records']
    data.extend(current_batch)

    # Move up the offset based on the batch size
    params['offset'] = params['offset'] + batch_size

    # Update last batch size
    last_batch_size = len(current_batch)
    print(f'Loaded batch with size {last_batch_size}')

# Convert to pandas dataframe
df = pd.DataFrame(data)

print("#---------- Extraction completed successfully ----------#")

#================================================== TRANSFORM ==================================================#

print("#-------------- Beginning transformation ---------------#")

# See notebook file for an explanation of the cleaning decisions

# Replace all instances of 'Not Available' with NA for consistency
df.replace('Not Available', pd.NA, inplace=True)

#-------------------- Cleaning INC_IR_NO --------------------#

print("Cleaning INC_IR_NO...")

# Convert to numeric type
df['INC_IR_NO'] = df['INC_IR_NO'].astype('Int64')

#-------------------- Cleaning INC_DATE ---------------------#

print("Cleaning INC_DATE...")

# Define a function to clean up date and convert it to pandas datetime format
def fix_INC_DATE(row):
  INC_DATE = row['INC_DATE']
  INC_TIME = row['INC_TIME']

  # If date is NA, do nothing
  if pd.isna(INC_DATE):
    return pd.NA

  # If INC_TIME exists
  if not pd.isna(INC_TIME):
    # Remove "T00:00:00" substring
    INC_DATE = INC_DATE.replace('T00:00:00', '')

    # Add the time from the INC_TIME column
    INC_DATE = INC_DATE + 'T' + INC_TIME + ':00'

  # Convert to date
  INC_DATE = pd.to_datetime(INC_DATE)

  return INC_DATE

# Apply the function to the INC_DATE column
df['INC_DATE'] = df.apply(fix_INC_DATE, axis=1)

#-------------------- Cleaning INC_YEAR ---------------------#

print("Cleaning INC_YEAR...")

# Convert year to numeric type
df['INC_YEAR'] = pd.to_numeric(df['INC_YEAR'])

#-------------------- Cleaning INC_TIME ---------------------#

print("Cleaning INC_TIME...")

# Define a function to extract the time from the cleaned date column
def fix_INC_TIME(row):
  if pd.isna(row['INC_DATE']):
    return pd.NA

  # Extract the time from INC_DATE and return it
  return row['INC_DATE'].time()

# Apply the function
df['INC_TIME'] = df.apply(fix_INC_TIME, axis=1)

#-------------------- Cleaning INC_BEAT ---------------------#

print("Cleaning INC_BEAT...")

# Define a function to clean up inconsistencies in the beat column
def fix_INC_BEAT(row):
  INC_BEAT = row['INC_BEAT']

  # For NA values, do nothing
  if pd.isna(INC_BEAT):
    return INC_BEAT

  # Remove `Beat` substring
  INC_BEAT = INC_BEAT.replace('Beat', '')

  # Also remove `(Airport)` substring
  INC_BEAT = INC_BEAT.replace('(Airport)', '')

  # Strip string
  INC_BEAT = INC_BEAT.strip()

  return INC_BEAT

# Apply the function
df['INC_BEAT'] = df.apply(fix_INC_BEAT, axis=1)

#-------------------- Cleaning INC_STATE --------------------#

print("Cleaning INC_STATE...")

# Set all values in the state column to AZ (since this is data for Phoenix, AZ)
df['INC_STATE'] = 'AZ'

#------------------ Cleaning INC_ZIPCODE --------------------#

print("Cleaning INC_ZIPCODE...")

# Convert to numeric format
df['INC_ZIPCODE'] = pd.to_numeric(df['INC_ZIPCODE'])

#------------------ Cleaning CIT_NUMBER ---------------------#

print("Cleaning CIT_NUMBER...")

# Convert to numeric format
df['CIT_NUMBER'] = pd.to_numeric(df['CIT_NUMBER'])

#--------------------- Cleaning CIT_AGE ---------------------#

print("Cleaning CIT_AGE...")

# Convert to numeric format
df['CIT_AGE'] = pd.to_numeric(df['CIT_AGE'])

# Define a function to remove invalid ages
def fix_CIT_AGE(row):
  CIT_AGE = row['CIT_AGE']

  # If age is < 0 or > 100, return NA
  if CIT_AGE < 0 or CIT_AGE > 100:
    return pd.NA

  return CIT_AGE

# Apply function
df['CIT_AGE'] = df.apply(fix_CIT_AGE, axis=1)

#------------------ Cleaning SUBJ_AGE_GROUP -----------------#

print("Cleaning SUBJ_AGE_GROUP...")

# Define a function to set age group based on the cleaned age column
def fix_SUBJ_AGE_GROUP(row):
  CIT_AGE = row['CIT_AGE']

  # If age is NA, return NA
  if pd.isna(CIT_AGE):
    return pd.NA
  elif CIT_AGE < 20:
    return '<20'
  elif CIT_AGE < 30:
    return '20s'
  elif CIT_AGE < 40:
    return '30s'
  elif CIT_AGE < 50:
    return '40s'
  elif CIT_AGE < 60:
    return '50s'
  elif CIT_AGE < 70:
    return '60s'
  elif CIT_AGE < 80:
    return '70s'
  elif CIT_AGE < 90:
    return '80s'

  return CIT_AGE

# Apply function
df['SUBJ_AGE_GROUP'] = df.apply(fix_SUBJ_AGE_GROUP, axis=1)

#--------------------- Cleaning CIT_RACE --------------------#

print("Cleaning CIT_RACE...")

# Define a function to handle redundant race values
def fix_CIT_RACE(row):
  CIT_RACE = row['CIT_RACE']

  # Do nothing for NA values
  if pd.isna(CIT_RACE):
    return CIT_RACE
  
  if 'whi' in CIT_RACE.lower():
    return 'White'
  elif 'black' in CIT_RACE.lower():
    return 'Black'
  elif 'asian' in CIT_RACE.lower():
    return 'Asian / Pacific Islander'
  elif 'unknown' in CIT_RACE.lower():
    return pd.NA

  return CIT_RACE

# Apply the function
df['CIT_RACE'] = df.apply(fix_CIT_RACE, axis=1)

#------------------ Cleaning CIT_ETHNICITY ------------------#

print("Cleaning CIT_ETHNICITY...")

# Define a function to handle redundant ethnicity values
def fix_CIT_ETHNICITY(row):
  CIT_ETHNICITY = row['CIT_ETHNICITY']

  # Do nothing for NA values
  if pd.isna(CIT_ETHNICITY):
    return CIT_ETHNICITY

  if 'non-hispanic' in CIT_ETHNICITY.lower() or 'not hispanic' in CIT_ETHNICITY.lower():
    return 'Non-Hispanic'
  elif 'hispanic' in CIT_ETHNICITY.lower() or 'h' in CIT_ETHNICITY.lower():
    return 'Hispanic'
  elif 'unknown' in CIT_ETHNICITY.lower():
    return pd.NA

  return CIT_ETHNICITY

# Apply the function
df['CIT_ETHNICITY'] = df.apply(fix_CIT_ETHNICITY, axis=1)

#------------------ Cleaning CITIZEN_CHARGE -----------------#

print("Cleaning CITIZEN_CHARGE...")

# Replacing 'None' with 'No Charge' to avoid confusion
df['CITIZEN_CHARGE'] = df['CITIZEN_CHARGE'].replace('None','No Charge')

#----------------- Cleaning SHOW_FORCE_COUNT ----------------#

print("Cleaning SHOW_FORCE_COUNT...")

# Convert to numeric format
df['SHOW_FORCE_COUNT'] = pd.to_numeric(df['SHOW_FORCE_COUNT'])

#---------------------------------------- Normalization ----------------------------------------#

# See notebook and ERD for normalization details

print("Normalizing dataframe...")

# Remove all rows that have null values for the intended primary keys
df.dropna(subset=['INC_IR_NO','CIT_NUMBER'],inplace=True)

# Replace pd.NA and np.nan with None
df.replace(pd.NA, None, inplace=True)
df.replace(np.nan, None, inplace=True)

# Get the columns that will be in each table
incident_report_cols = ['INC_IR_NO','INC_IA_NO','INC_DATE','INC_YEAR','INC_TIME','INC_DAY_WEEK','INC_BEAT','HUNDRED_BLOCK',
                        'INC_CITY','INC_STATE','INC_ZIPCODE','INC_PRECINCT','HIGHEST_SHOW_FORCE','SHOW_FORCE_COUNT']
citizen_cols = ['CIT_NUMBER','CIT_GENDER','CIT_AGE','SUBJ_AGE_GROUP','CIT_RACE','CIT_ETHNICITY','SIMPLE_SUBJ_RE_GRP']
incident_details_cols = ['INC_IR_NO','CIT_NUMBER','CITIZEN_CHARGE']

# Split the dataframe into the three tables
df_incident_reports = df[incident_report_cols].drop_duplicates().reset_index(drop=True)
df_citizens = df[citizen_cols].drop_duplicates().reset_index(drop=True)
df_incident_details = df[incident_details_cols].drop_duplicates().reset_index(drop=True)

# Rename columns to be more readable
df_incident_reports.rename(columns={
    'INC_IR_NO':'incident_report_num',
    'INC_IA_NO':'show_of_force_report_num',
    'INC_DATE':'date',
    'INC_YEAR':'year',
    'INC_TIME':'time',
    'INC_DAY_WEEK':'day',
    'INC_BEAT':'beat',
    'HUNDRED_BLOCK':'address',
    'INC_CITY':'city',
    'INC_STATE':'state',
    'INC_ZIPCODE':'zipcode',
    'INC_PRECINCT':'precinct',
    'HIGHEST_SHOW_FORCE':'highest_show_of_force',
    'SHOW_FORCE_COUNT':'show_of_force_count'
},inplace=True)

df_citizens.rename(columns={
    'CIT_NUMBER':'citizen_num',
    'CIT_GENDER':'gender',
    'CIT_AGE':'age',
    'SUBJ_AGE_GROUP':'age_group',
    'CIT_RACE':'race',
    'CIT_ETHNICITY':'ethnicity',
    'SIMPLE_SUBJ_RE_GRP':'race_ethnicity_group'
}, inplace=True)

df_incident_details.rename(columns={
    'INC_IR_NO':'incident_report_num',
    'CIT_NUMBER':'citizen_num',
    'CITIZEN_CHARGE':'citizen_charge'
}, inplace=True)

# Add ID column
df_incident_details.insert(0,'incident_detail_num',df_incident_details.index + 1)

print("#-------- Transformation completed successfully --------#")

#===================================================== LOAD ====================================================#

print("#----------------- Beginning loading -------------------#")

# Load .env file (not needed in Docker Compose)
#load_dotenv(find_dotenv(), verbose=True)

# Get database parameters
DB_PARAMS = {
    "dbname": os.getenv("POSTGRES_DB"), 
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT")
}

# Helper function to create DB connection
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("Database Connection Successful\n")
        return conn
    except Exception as e:
        print(f'Error Connecting to Database: {e}')

# Connect to DB
conn = get_db_connection()
cursor = conn.cursor()

# Create query to create the required tables
query = '''
BEGIN;

CREATE TABLE IF NOT EXISTS public.incident_reports
(
    incident_report_num bigint NOT NULL,
    show_of_force_report_num text,
    date date,
    year integer,
    "time" time without time zone,
    day text,
    beat text,
    address text,
    city text,
    state text,
    zipcode integer,
    precinct text,
    highest_show_of_force text,
    show_of_force_count integer,
    PRIMARY KEY (incident_report_num)
);

CREATE TABLE IF NOT EXISTS public.citizens
(
    citizen_num integer NOT NULL,
    gender text,
    age integer,
    age_group text,
    race text,
    ethnicity text,
    race_ethnicity_group text,
    PRIMARY KEY (citizen_num)
);

CREATE TABLE IF NOT EXISTS public.incident_details
(
    incident_detail_num integer NOT NULL,
    incident_report_num bigint NOT NULL,
    citizen_num integer NOT NULL,
    citizen_charge text,
    PRIMARY KEY (incident_detail_num)
);

ALTER TABLE IF EXISTS public.incident_details
    ADD FOREIGN KEY (incident_report_num)
    REFERENCES public.incident_reports (incident_report_num) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS public.incident_details
    ADD FOREIGN KEY (citizen_num)
    REFERENCES public.citizens (citizen_num) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

END;
'''

# Execute table creation query
cursor.execute(query)

print('Tables Created Successfully\n')

conn.commit()

# Insert rows into all three tables

print("Beginning insertion into incident reports table...")

# Loop over all incident reports
for _, row in df_incident_reports.iterrows():
    # Insert current row - do nothing if the row already exists in the database
    cursor.execute('INSERT INTO incident_reports VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;',
                (row['incident_report_num'],row['show_of_force_report_num'],row['date'],row['year'],row['time'],
                row['day'],row['beat'],row['address'],row['city'],row['state'],row['zipcode'],row['precinct'],
                row['highest_show_of_force'],row['show_of_force_count']))

print("Successfully inserted into incident reports table\n")

print("Beginning insertion into citizens table...")

# Loop over all citizens
for _, row in df_citizens.iterrows():
    # Insert current row - do nothing if the row already exists in the database
    cursor.execute('INSERT INTO citizens VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;',
                (row['citizen_num'],row['gender'],row['age'],row['age_group'],row['race'],
                row['ethnicity'],row['race_ethnicity_group']))

print("Successfully inserted into citizens table\n")

print("Beginning insertion into incident_details table...")

# Loop over all incident details
for _, row in df_incident_details.iterrows():
    # Insert current row - do nothing if the row already exists in the database
    cursor.execute('INSERT INTO incident_details VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;',
                (row['incident_detail_num'],row['incident_report_num'],row['citizen_num'],row['citizen_charge']))
    
print("Successfully inserted into incident_details table\n")

print("All insertions completed successfully")

conn.commit()
cursor.close()
conn.close()

print("#----------- Loading completed successfully ------------#")