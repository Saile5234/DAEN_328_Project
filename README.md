# DAEN 328 Final Project

## Setup

First, go to pgAdmin4 and create a database to hold the data. There's no need to add any tables since the notebook will do that automatically. Remember the database name for the next steps.

For Python, we'll use the DAEN 328 virtual environment that we've been using the entire semester. We just need one additional package to access read from the ```.env``` file. Activate the virtual environment and run:

```bash
pip install python-dotenv
```

Next, we can create the ```.env``` file itself. Create a file named ```.env``` in the project directory and add the following lines:

```bash
POSTGRES_DB=ProjectDB
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOURPASSWORD
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Replace the fields with your database name, username, and password.

You're now all set up. To make sure everything was done correctly, try running the pipeline as shown in the next section.

## Running the Pipeline

First, open the ```DAEN_328_Data_Pipeline_Phoenix_Project.ipynb``` file. This notebook:

* Loads the data from the API (or the CSV if it's already saved locally)
* Cleans the data
* Adjusts types
* Normalizes the data in accordance with the ERD
* Renames the columns to be more readable
* Creates the tables in the database (if they don't exist already)
* Inserts the data into those tables

Simply hit "Run All" to run the entire pipeline. If you encounter an error, you should probably panic.

Once this is done, you can run the Streamlit dashboard. Open your terminal (make sure the virtual environment is activated) and enter:
```shell
streamlit run app.py
```

You should now be able to see the dashboard and analyze the data.