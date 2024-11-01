
import os
import re
import logging

from airflow import DAG
from datetime import datetime

from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from ingest_script_local import ingest_callable


#set up logging
logger = logging.getLogger(__name__)

AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")

DATASET_FILE = "yellow_tripdata_2021-01.csv.gz"
DATASET_DATE = re.sub('yellow_tripdata_', '', DATASET_FILE)
URL_PREFIX = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow' 
URL_TEMPLATE = f"{URL_PREFIX}/{DATASET_FILE}"
#URL_TEMPLATE = URL_PREFIX + '/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv'
OUTPUT_FILE_TEMPLATE = f'{AIRFLOW_HOME}/output_{DATASET_FILE}'
TABLE_NAME_TEMPLATE = f'yellow_taxi_{DATASET_DATE}'

PG_USER = os.getenv('POSTGRES_USER')
PG_PASSWORD = os.getenv('POSTGRES_PASSWORD')
#PG_HOST = os.getenv('PG_HOST')
#host is the default value of 'postgres' for our purposes
PG_HOST = 'postgres'
#PG_PORT = os.getenv('POSTGRES_PORT')
#From the docker-compose yaml, port is '5432'
PG_PORT = 5432
PG_DATABASE = os.getenv('POSTGRES_DB')

#print env variables
logger.info('Passing PG_USER: %s, PG_PASSWORD: %s, PG_HOST: %s, PG_PORT: %s, PG_DATABASE: %s', 
            PG_USER, PG_PASSWORD, PG_HOST, PG_PORT, PG_DATABASE)

with DAG('LocalIngestionDag', 
         start_date=datetime(2021,1,1),
         schedule_interval="0 6 2 * *",
         catchup=False) as dag:
    wget_task = BashOperator(
        task_id='wget',
        bash_command=f'curl -sSL {URL_TEMPLATE} > {OUTPUT_FILE_TEMPLATE}'
    )

    ingest_task = PythonOperator(
        task_id='ingest',
        python_callable=ingest_callable,
        op_kwargs=dict(user=PG_USER,
                       password=PG_PASSWORD,
                       host=PG_HOST,
                       port=PG_PORT,
                       db=PG_DATABASE,
                       table_name = TABLE_NAME_TEMPLATE,
                       csv_file=OUTPUT_FILE_TEMPLATE
                       )
    )

    wget_task >> ingest_task