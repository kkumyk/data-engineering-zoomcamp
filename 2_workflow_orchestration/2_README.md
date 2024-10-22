
# Orchestration with Airflow

## Introduction to Workflow Orchestration

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

## Airflow Architecture 
Components of a typical Airflow installation:

- <i><b>scheduler</i></b>
    - is Airflow's "core"
    - handles:
        1. triggering scheduled workflows
        2. submitting tasks to the executor to run

- <i><b>executor</i></b>
    - handles running tasks
    - in a default installation, runs everything inside the scheduler
    - but most production-suitable executors push task execution out to workers

- <i><b>worker</i></b>
    - executes tasks given by the scheduler

- <i><b>webserver</i></b> serves as the GUI

- <i><b>DAG directory</i></b>
    - a folder with DAG files which is read by the scheduler and the executor (and by extension of any worker the executor might have)

- <i><b>metadata database</i></b>
    - (Postgres) used by the scheduler, the executor and the web server to store state
    - the backend of Airflow

<i><b>Additional components</i></b>:
- <code>redis</code>: a message broker that forwards messages from the scheduler to workers.
- <code>flower</code>: app for monitoring the environment, available at port 5555 by default.
- <code>airflow-init</code>: initialization service which we will customize for our needs.

Airflow creates a folder structure when running:

- ./dags - DAG_FOLDER for DAG files
- ./logs - contains logs from task execution and scheduler.
- ./plugins - for custom plugins

### Further Definitions:

<b>DAG (Directed Acyclic Graph)</b>:
    -specifies the dependencies between a set of tasks with explicit execution order
    - has a beginning as well as an end: "acyclic".

A DAG's Structure:
- DAG Definition
- Tasks (eg. Operators)
- Task Dependencies (control flow: >> or << )

<b>DAG Run</b>:
- individual execution/run of a DAG.
- may be scheduled or triggered.

<b>Task</b>:
- a defined unit of work. 
- describes what to do, be it fetching data, running analysis, triggering other systems etc.

Common Task Types:
- <i><b>Operators</i></b> are predefined tasks - most common.
- <i><b>Sensors</i></b> are a subclass of operator which wait for external events to happen.
- <i><b>TaskFlow decorators</i></b> (subclasses of Airflow's BaseOperator) are custom Python functions packaged as tasks.
lugins - for custom plugins
<b>Task Instance</b>:
- an individual run of a single task.
- has an indicative state, which could be running, success, failed, skipped, up for retry, etc.
    - Ideally, a task should flow from none, to scheduled, to queued, to running, and finally to success.

## Setting up Airflow with Docker

### Prerequisites

1. Rename the service account credentials JSON file to named google_credentials.json
```bash
cd ~
mkdir -p ~/.google/credentials/
mv /your/path/to-downloaded-file/google_credentials.json ~/.google/credentials/google_credentials.json
```

## Ingesting Data to Local Postgres with Airflow
Main Goal:
- Converting the ingestion script for loading data to Postgres to Airflow DAG

Learning Sources:

- [Ingesting Data to Local Postgres with Airflow](https://www.youtube.com/watch?v=s2U8MWJH5xA&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb)






</br>
</hr>

## Learning Materials Used

[Data Ingestion](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/cohorts/2022/week_2_data_ingestion)
[Introduction to Workflow Orchestration](https://www.youtube.com/watch?v=0yK7LXwYeD0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=18) (video)

[Setup Airflow Environment with Docker-Compose](https://www.youtube.com/watch?v=lqDMzReAtrw&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=19) (video)

[Local Setup for Airflow](https://www.youtube.com/watch?v=A1p5LQ0zzaQ) (video)

[Ingesting Data to Local Postgres with Airflow](https://www.youtube.com/watch?v=s2U8MWJH5xA) (video)

[Alvaro Navas's Course Notes](https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/2_data_ingestion.md#data-ingestion)