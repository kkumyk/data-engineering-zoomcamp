
# Analytics Engineering

## Prerequisites

1. a running warehouse (BigQuery or Postgres)
2. a set of running pipelines ingesting the project dataset (week 3 completed)

    The following datasets ingested from the course [Datasets list](https://github.com/DataTalksClub/nyc-tlc-data/):
    - Yellow taxi data - Years 2019 and 2020
    - Green taxi data - Years 2019 and 2020
    - fhv data - Year 2019.

    <i>Note</i> that there are two ways available to load data files quicker directly to GCS, without Airflow: [option 1](https://www.youtube.com/watch?v=Mork172sK_c&list=PLaNLNpjZpzwgneiI-Gl8df8GCsPYp_6Bs) and [option 2](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse/extras) via [web_to_gcs.py script](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/03-data-warehouse/extras/web_to_gcs.py).

    However, if you've completed modules 1-3, the above data should be already be found in your BigQuery account.

    Starting with checking the file uploads done in the previous modules is a good exercise for reviewing of what was done in the previous three modules.

    In my case, to shorted the time spent for uploading the files, I've uploaded the files for the three taxi types for the first half of 2021.

    The prerequisites in module 4 require the data for 2019 and 2020 as this module using Airflow for orchestration was done a couple of years ago. The FHV data for 2019 was requested for the homework completion. I decided to first focus on uploads for the Yellow and Green data as it looks like these will be used throughout the module.

    To upload these files I run the [data_ingestion_gcs_multiFile.py dag](https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/2_workflow_orchestration/airflow_gcp/dags/data_ingestion_gcs_multiFile.py) from the airflow_gcp folder by first adjusting the start and the end dates and commenting out the tasks focusing on fhv file uploads. The result was that all files apart from the three months's data in 2019 for the Yellow taxi type were not uploaded, see below: 

    <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/yellow_taxi_data_three_workflows_failed.png" alt="DAG run result in Airflow for multiple files - three failed" width="600"/>

    I saw this as a good opportunity to test the [data_ingestion_gcs.py (uploads a single file to GCS)](https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/2_workflow_orchestration/airflow_gcp/dags/data_ingestion_gcs.py). I run this dag for the missing three files. They will first end in the GCS bucket on the same level as the taxi types folders, see below the uploaded file for May 2019:
    
    <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/yellow_2019_05_file_upload.png" alt="DAG run result - a single file upload to GCS bucket" width="600"/>

    Each file was then moved manually from the bucket to the corresponding taxi type/year folder. All in one, it looks like the work done in the previous three modules was not in vein and I have the data required to continue with the material from ANalytics Engineering module of the course. :) 

