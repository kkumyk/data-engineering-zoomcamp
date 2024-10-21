
# Orchestration with Airflow

How <b>NOT</b> to create a data pipeline:
- write a script that
- downloads a CSV
- processes it to ingest data to Postgres.

Why not?

- the script contains 2 steps which should be split into two files to handle downloading and processing data separately:
```bash
(web) → DOWNLOAD → (csv) → INGEST → (Postgres)
```

This is because:

- if our internet connection is slow or if we're simply testing the script, it will have to download the CSV file every single time that we run the script, which is less than ideal.

Data Workflow / Directed Acyclic Graph (DAG) for this Module's Data Pipeline:
```bash
(web) # dependency for the first job
  ↓
  DOWNLOAD # job
  ↓
(csv) # prev job's output / dependency for the next job
  ↓
  PARQUETIZE # job
  ↓
(parquet) # prev job's output / dependency for the next job
  ↓
  UPLOAD TO GCS # job
  ↓
(parquet in GCS) # prev job's output / dependency for the next job
  ↓
  UPLOAD TO BIGQUERY # job
  ↓
(table in BQ) # final result
```
- DAG lacks any loops and the data flow is well defined.

- Jobs' params:
    - can be different for some jobs or sbe shared between jobs;
    - there may also be global parameters which are the same for all of the jobs.

- A Workflow Orchestration Tool (e.g.: [Apache Airflow](https://airflow.apache.org/)) allows us:
    - to define data workflows and parametrize them;
    - provides additional tools such as history and logging.


</hr>

## Learning Materials 

[ video source: 2.2.1 - Introduction to Workflow Orcown set of parameters and 
<!-- [ video source: 2.3.1 - Setup Airflow Environment with Docker-Compose](https://www.youtube.com/watch?v=lqDMzReAtrw)

[ video source: 2.3.2 - Ingesting Data to GCP with Airflow](https://www.youtube.com/watch?v=9ksX9REfL8w) -->

[ video source: 2.3.4 - Local Setup for Airflow](https://www.youtube.com/watch?v=A1p5LQ0zzaQ)

[ video source: 2.3.3 - Ingesting Data to Local Postgres with Airflow](https://www.youtube.com/watch?v=s2U8MWJH5xA)

[Alvaro Navas's Notes](https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/2_data_ingestion.md#data-ingestion)