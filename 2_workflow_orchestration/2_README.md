
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
2. <code>docker-compose</code> should be at least version v2.x+ and Docker Engine should have at least 5GB of RAM available, ideally 8GB. On Docker Desktop this can be changed in Preferences > Resources.

    <summary>Upgrading Docker Compose to v2.x+ on Ubuntu 23.10 (see details below)
        <details>

    #### Upgrading Docker Compose to v2.x+ on Ubuntu 23.10
    1. Remove installed <code>docker-compose</code>
    - <code>docker-compose</code> binary was previously installed via a package manager (apt) and is located at:
    ```bash
    which docker-compose
    /usr/bin/docker-compose
    ``` 
    - to remove it, run:
    ```bash
    sudo apt remove docker-compose
    ```
    2. Install Docker Compose v2.x as part of Docker Engine
    - Docker Compose v2 is now distributed as part of Docker Engine, so we don't need to install it separately anymore. To get Docker Compose v2.x:
        - install Docker Engine (if not installed):
        ```bash
        sudo apt-get update
        sudo apt-get install \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        ```
        - add Docker's official GPG key:
        ```bash
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.gpg > /dev/null
        ```
        - set up the repository:
        ```bash
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        ```
        - install Docker Engine, CLI, and Docker Compose:
        ```bash
        sudo apt-get update
        sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        ```
        - verify installation by accessed using the new <code>docker compose</code> (with a space):
        ```bash
        docker compose version
        ```
    </details>
</summary>

2. Create a new <code>airflow</code> subdirectory in your work directory.

### docker-compose.yaml update
>>>> By following steps below you will create and update a docker-compose.yaml file to run that only runs the web server and the scheduler and runs the DAGs in the scheduler rather than running them in external workers:

3. Download the official Docker-compose YAML file for the latest Airflow version. 
    ```bash
    curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.2/docker-compose.yaml'
    ```
4. [Set up the Airflow user](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#setting-the-right-airflow-user) and create and <code>.env</code> with the appropriate UID (for all operating systems other than MacOS):
    ```bash
    echo -e "AIRFLOW_UID=$(id -u)" > .env
    ```
5. The base Airflow Docker image won't work with GCP. Adjust the file or download a GCP-ready Airflow Dockerfile from [this link]() TODO.

6. Add requirements.txt file and add:
    ```bash
    apache-airflow-providers-google # allows Airflow using the GCP SDK
    pyarrow # a library to work with parquet files
    ```
7. Alter the x-airflow-common service definition inside the docker-compose.yaml:
    - point to our custom Docker image:
        1. comment or delete the image field:
            ```bash
            # image: ${AIRFLOW_IMAGE_NAME:-apache/airflow:2.10.2}
            ```
        2. uncomment the build line, or use the following (make sure you respect YAML indentation):
            ```bash
              build:
                context: .
                dockerfile: ./Dockerfile
            ```
        3. Add a volume and point it to the folder where you stored the credentials json file (see prerequisites section above):
            ```bash
            - ~/.google/credentials/:/.google/credentials:ro
            ```
        4. Add 2 new environment variables right after the others: GOOGLE_APPLICATION_CREDENTIALS and AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT:
            ```bash
            GOOGLE_APPLICATION_CREDENTIALS: /.google/credentials/google_credentials.json
            AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT: 'google-cloud-platform://?extra__google_cloud_platform__key_path=/.google/credentials/google_credentials.json'
            ```
        5. Add 2 new additional environment variables for your GCP project ID and the GCP bucket that Terraform should have created in the previous lesson. You can find this info in your GCP project's dashboard:
            ```bash
            GCP_PROJECT_ID: '<your_gcp_project_id>'
            GCP_GCS_BUCKET: '<your_bucket_id>'
            ```Execution
9. Change the AIRFLOW__CORE__EXECUTOR environment variable from CeleryExecutor to LocalExecutor.

10. At the end of the x-airflow-common definition, within the depends-on block, remove these 2 lines:
    ```yaml
    redis:
       condition: service_healthy
    ```
11. Comment out the AIRFLOW__CELERY__RESULT_BACKEND and AIRFLOW__CELERY__BROKER_URL environment variables.

### Execution

1. <b>Build the image (may take several minutes).</b> Only needs to be done when:
    - running Airflow for first time,
    - if you modified the Dockerfile or the requirements.txt file.

    ```bash
    docker compose build
    ```
2. <b>Initialize configs.</b>
    ```bash
    docker compose up airflow-init
    ```
3. <b>Run Airflow</b>
    ```bash
    docker compose up -d
    ```
4. Access the Airflow GUI by browsing to localhost:8080.
    - Username and password are both airflow by default.


<!-- ## Ingesting Data to Local Postgres with Airflow
Main Goal:
- Converting the ingestion script for loading data to Postgres to Airflow DAG

Learning Sources:

- [Ingesting Data to Local Postgres with Airflow](https://www.youtube.com/watch?v=s2U8MWJH5xA&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb) -->


<!-- to log into the db
 psql -h localhost -p 5432 -U taxi_driver -d ny_taxi -->

<!-- TODOs:
- two ingest files
- update env with db creda library to work with parquet filesdata ingesting local: 55:43
- combine containers in one network: 1:00 -->



</br>
</hr>

## Learning Materials Used

[Data Ingestion](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/cohorts/2022/week_2_data_ingestion)
[Introduction to Workflow Orchestration](https://www.youtube.com/watch?v=0yK7LXwYeD0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=18) (video)

[Setup Airflow Environment with Docker-Compose](https://www.youtube.com/watch?v=lqDMzReAtrw&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=19) (video)

[Local Setup for Airflow](https://www.youtube.com/watch?v=A1p5LQ0zzaQ) (video)

[Ingesting Data to Local Postgres with Airflow](https://www.youtube.com/watch?v=s2U8MWJH5xA) (video)

[Alvaro Navas's Course Notes](https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/2_data_ingestion.md#data-ingestion)