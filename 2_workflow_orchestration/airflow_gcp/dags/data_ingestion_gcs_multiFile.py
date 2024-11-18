import os
import logging
from datetime import datetime

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq
from google.cloud import storage

#set up logging
logger = logging.getLogger(__name__)

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")

#GCP environment variables
BUCKET=os.environ.get("GCP_GCS_BUCKET")
logger.info(f'{BUCKET} is the bucket.')

#set default args for the dag
default_args = {
    "owner": "admin",
    "depends_on_past": False,
    "retries": 1,
}

def format_to_parquet(src_file, dest_file):
    if not (src_file.endswith('.csv') or src_file.endswith('.csv.gz')):
        logger.error("Can only accept source files in CSV format, for the moment")
        return
    table = pv.read_csv(src_file)
    pq.write_table(table, dest_file)

def upload_to_gcs(bucket, object_name, local_file):
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB

    client = storage.Client()
    bucket = client.get_bucket(bucket)

    blob = bucket.blob(object_name)
    logger.info(f'Blob is {blob}')
    blob.upload_from_filename(local_file)

def download_convert_upload_dag(dag,
                                url_template, 
                                output_template, 
                                parquet_file, 
                                gcs_path_template):
        
        with dag:             
            download_dataset_task = BashOperator(
                task_id="download_dataset_task",
                bash_command=f"curl -sSLf {url_template} > {output_template}"
            )

            format_to_parquet_task = PythonOperator(
                task_id="format_to_parquet_task",
                python_callable=format_to_parquet,
                op_kwargs={
                    "src_file": output_template,
                    "dest_file": parquet_file
                }
            )

            local_to_gcs_task = PythonOperator(
                task_id="local_to_gcs_task",
                python_callable=upload_to_gcs,
                op_kwargs={
                    "bucket": BUCKET,
                    "object_name": gcs_path_template,
                    "local_file": parquet_file
                }
            )

            purge_task = BashOperator(
                task_id="purge_task",
                bash_command=f"rm {output_template} {parquet_file}"
                )
            
            download_dataset_task >> format_to_parquet_task >> local_to_gcs_task >> purge_task

#yellow taxi data:
yellow_url_prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
yellow_url_template = yellow_url_prefix + 'yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv.gz'
yellow_output_template = path_to_local_home + '/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv.gz'
yellow_parquet_file = path_to_local_home + '/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
yellow_gcs_path_template = 'raw/yellow_tripdata/{{ execution_date.strftime(\'%Y\') }}/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'

yellow_taxi_data_dag = DAG(
     dag_id="yellow_taxi_data",
     start_date=datetime(2021, 1, 1),  # Adjusted to start from January 1, 2021
     end_date=datetime(2021, 7, 31),  # Adjusted to end on July 31, 2021
     schedule_interval="0 6 2 * *",  # Runs on the 2nd day of each month at 6 AM
     default_args=default_args,
     catchup=True,  # Optional, depending on how you want to handle past dates
     max_active_runs=3,
     tags=['dtc-de']
)

download_convert_upload_dag(dag=yellow_taxi_data_dag, 
                            url_template=yellow_url_template,
                            output_template=yellow_output_template,
                            parquet_file=yellow_parquet_file,
                            gcs_path_template=yellow_gcs_path_template)


#green taxi data:
green_url_prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/'
green_url_template = green_url_prefix + 'green_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv.gz'
green_output_template = path_to_local_home + '/green_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv.gz'
green_parquet_file = path_to_local_home + '/green_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
green_gcs_path_template = 'raw/green_tripdata/{{ execution_date.strftime(\'%Y\') }}/green_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'

green_taxi_data_dag = DAG(
     dag_id="green_taxi_data",
     start_date=datetime(2021, 1, 1),  # Adjusted to start from January 1, 2021
     end_date=datetime(2021, 7, 31),  # Adjusted to end on July 31, 2021
     schedule_interval="30 6 2 * *",  # Runs on the 2nd day of each month at 6:30 AM
     default_args=default_args,
     catchup=True,  # Optional, depending on how you want to handle past dates
     max_active_runs=3,
     tags=['dtc-de']
)

download_convert_upload_dag(dag=green_taxi_data_dag, 
                            url_template=green_url_template,
                            output_template=green_output_template,
                            parquet_file=green_parquet_file,
                            gcs_path_template=green_gcs_path_template)


#fhv taxi data:
fhv_url_prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/'
fhv_url_template = fhv_url_prefix + 'fhv_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv.gz'
fhv_output_template = path_to_local_home + '/fhv_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv.gz'
fhv_parquet_file = path_to_local_home + '/fhv_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
fhv_gcs_path_template = 'raw/fhv_tripdata/{{ execution_date.strftime(\'%Y\') }}/fhv_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'

fhv_taxi_data_dag = DAG(
     dag_id="fhv_taxi_data",
     start_date=datetime(2021, 1, 1),  # Adjusted to start from January 1, 2021
     end_date=datetime(2021, 7, 31),  # Adjusted to end on July 31, 2021
     schedule_interval="0 7 2 * *",  # Runs on the 2nd day of each month at 7 AM
     default_args=default_args,
     catchup=True,  # Optional, depending on how you want to handle past dates
     max_active_runs=3,
     tags=['dtc-de']
)

download_convert_upload_dag(dag=fhv_taxi_data_dag, 
                            url_template=fhv_url_template,
                            output_template=fhv_output_template,
                            parquet_file=fhv_parquet_file,
                            gcs_path_template=fhv_gcs_path_template)


# #zone taxi data:
# zone_url_prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/'
# zone_url_template = zone_url_prefix + 'taxi_zone_lookup.csv'
# zone_output_template = path_to_local_home + '/taxi_zone_lookup.csv'
# zone_parquet_file = path_to_local_home + '/taxi_zone_lookup.parquet'
# zone_gcs_path_template = 'raw/taxi_zone/taxi_zone_lookup.parquet'

# taxi_zone_data_dag = DAG(
#      dag_id="taxi_zone_data",
#      start_date=days_ago(1),
#      schedule_interval="@once",
#      default_args=default_args,
#      catchup=True,
#      max_active_runs=3,
#      tags=['dtc-de']
# )

# download_convert_upload_dag(dag=taxi_zone_data_dag, 
#                             url_template=zone_url_template,
#                             output_template=zone_output_template,
#                             parquet_file=zone_parquet_file,
#                             gcs_path_template=zone_gcs_path_template)