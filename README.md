# DAEN 328 Final Project

By Elias Ortiz, Bobby Cuellar, Brody Mitchell, and Jay Yan

## Introduction

This repository contains a dockerized batch-loaded data pipeline that loads and presents data from the City of Phoenix Police Officer Show of Force dataset, which can be found at the following link:
https://www.phoenixopendata.com/dataset/officer-show-of-force/resource/7e9d5fc7-ce02-4108-80af-369b1b54c4ff

The online database consists of a single table where each row is a single show of force incident report. For context, a "show of force" is a event where a police officer attempts to gain compliance by demonstrating authority without immediately resorting to physical force. This database specifically focuses on incidents where a Phoenix police officer pointed a weapon system (a firearm or non-lethal weapon) at or in the direction of a suspect. Each incident includes the location, time, show of force type (what type of weapon), as well as various characteristics of the suspect (age, race, gender, etc.). We chose this dataset because it offers a number of avenues for analysis. For instance, much of our analysis was focused on at the distribution of show of force incidents (and what types of incidents) across various suspect demographics to see if there were any noticeable trends. These types of analyses let us observe if there are any potential biases that indicate that a situation is more likely to lead to a show of force incident.

## Pipeline Description and Repository Layout
The pipeline loads the data from the online API, cleans/transforms it into a normalized format (as shown in the ERD), and then loads the data into a PostgreSQL database. The contents of this database are then displayed using a Streamlit dashboard containing a number of interactive visualizations.

The contributions of each team member can be found below:
| Team Member | Contributions |
| --- | --- |
| Elias Ortiz | repository setup, ETL script creation, dockerization setup, README creation |
| Bobby Cuellar | Initial ERD and schema formulation, Primary streamlit dashboard creation, presentation creation |
| Brody Mitchell | ERD and schema formulation, Streamlit dashboard creation, presentation creation |
| Jay Yan | ERD and schema formulation, Streamlit dashboard creation |

Explanations for each of the files in the database can be found below:

| File | Description | Author |
| --- | --- | --- |
| app.py | Python script handling the Streamlit dashboard and all queries/visualizations contained therein | Elias Ortiz, Bobby Cuellar, Jay Yan, Brody Mitchell |
| docker-compose.yaml | Docker compose file | Elias Ortiz |
| Dockerfile.app | Dockerfile for app.py | Elias Ortiz |
| Dockerfile.ETL | Dockerfile for ETL.py | Elias Ortiz |
| ERD.png | Image of the ERD used for this dataset | Elias Ortiz |
| ETL.py | Python script handling the Extraction of the data from the online API, its Transformation into a readable/normalized format, and Loading it into the PostgreSQL database | Elias Ortiz |
| ETL_workspace.ipynb | Testing workspace for setting up the ETL process; contains explanations of the thought process and logic behind the decisions made | Elias Ortiz |
| project_ERD.pgerd | pgAdmin4 ERD file for the ERD shown in ERD.png | Elias Ortiz |
| README.md | Explanatory information and instructions | Elias Ortiz |
| requirements.txt | Required python packages that are automatically installed by the pipeline | N/A |

## Setup

The only setup step is to create the ```.env``` file that will be used by the pipeline. The template ```.env.sample``` is provided, so you just need to create a copy of it and rename it to ```.env```.

Replace the value of ```POSTGRES_PASSWORD``` with your PostgreSQL password. You can leave the other fields as they are.

You're now all set up. To make sure everything was done correctly, try running the pipeline as shown in the next section.

## Running the Pipeline

1. First, open the Docker Desktop application to start up docker.
2. Next, open a terminal or command prompt and navigate to the project directory.
3. Next, enter ```docker compose up --build``` to build and run the pipeline.
4. Wait for the pipeline to start up - this may take a while if it's your first time.
5. Wait for the ETL process to complete. When you see "You can now view your Streamlit app in your browser.", you can use the following link to access the dashboard: http://localhost:8501
6. You should now be able to see the dashboard and analyze the data.
7. When finished, return to the terminal and enter ```docker compose down -v``` to terminate the pipeline and delete any data volumes.
