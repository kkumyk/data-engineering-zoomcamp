Table of Contents:

[Orchestration with Airflow](#orchestration-with-airflow)

[ETL Using Airflow and Postgres in a Docker Container Locally](#etl-using-airflow-and-postgres-in-a-docker-container-locally)

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


## ETL Using Airflow and Postgres in a Docker Container Locally

This project shows how to:
1. run Airflow using LocalExecutor
    - <i>the entire workflow is orchestrated using Airflow</i>
2. download data from a website
    - <i>a Python script downloads a .csv file from a website
    - the Postgres db is accessed via pgAdmin</i>
3. upload data to a Postgres database running in a Docker container
    - <i>a Python script uploads downloaded data to a postgres db.</i>

```bash
# Project Structure

airflow_local
    ├── dags
    │   ├── data_ingestion_local.py
    │   └── ingest_script_local.py
    ├── logs
    ├── scripts
    │    ├── entrypoint.sh*
    ├── .env
    ├── docker-compose.yaml
    ├── Dockerfile
    └── requirements.txt
```
\* <i>entrypoint.sh</i>

- contains the list of executables that will always run after the container is initiated
- the exec line that executes webserver and scheduler has to be written so that both the exec commands are in one single line as splitting the two exec commands does not run the scheduler
- airflow username and login details are the credentials used to log into airflow web UI.

### Running Airflow Locally via Docker
1. Build docker compose image

    Make sure your Docker Desktop is running. From inside the airflow directory, build the <code>docker compose image</code>:

    ```bash
    docker compose build
    ```
2. Run docker-compose in detached mode:
    ```bash
    docker-compose up -d
    ```
    This spins up 4 containers:
    - postgres database
    - pgAdmin
    - airflow webserver
    - airflow scheduler

    Verify with <code>docker ps</code> command.

3. Open Airflow Web UI:
    - type the port address in a web browser as specified in docker compose file
    - log in with the credentials specified during the docker/airflow set up process in the <code>entrypoint.sh</code> file. E.g:
        <i>
        - localhost:8080
        - user=admin
        - password=admin</i>
    
    When you log in, your dag should show up on the home page. Click on the dag name and hit the little right-arrow icon on the right side to trigger dag. Your dag is now running.

4. Inspect Your Postgres Database in pgAdmin
    - log into pgAdmin in a browser using the port number and credentials you specified during docker/pgAdmin. E.g.:
        <i>
        - localhost:5050
        - user=admin@admin.com
        - password=root</i>
    
    - register a new server, login creds are those of the postgres db we specified in the <code>docker-compose yaml</code> via <code>.env</code> file:

        <i>
    - .env:
        
        - POSTGRES_USER=postgres
        - POSTGRES_PASSWORD=postgres
        - POSTGRES_DB=airflow

    - creds for the server registration:
        - host name / address: postgres (as the name of the service specified in docker compose file)
        - user: postgres
        - password: postgres
        - db name: airflow </i>

### DAGs

#### Creating a DAG

- A DAG (Directed Acyclic Graph) is the core concept of Airflow, collecting Tasks together, organized with dependencies and relationships to say how they should run.
- A DAG is created as a Python script which imports a series of libraries from Airflow.
- There are 3 different ways of declaring a DAG. e.g.: using a context manager
- When declaring a DAG we must provide at least a <code>dag_id</code> parameter. 
- The content of the DAG is composed of tasks. The example <i>- a DAG created using a context manager - </i> contains 2 operators, which are predefined tasks provided by Airflow's libraries and plugins.
    - An operator only has to be declared with any parameters that it may require.
    - There is no need to define anything inside them.
    - All operators must have at least a task_id parameter.
    ```bash
    with DAG(dag_id="my_dag_name") as dag:
    op1 = DummyOperator(task_id="task1")
    op2 = DummyOperator(task_id="task2")
    op1 >> op2
    ```
- At the end of the definition we define the task dependencies, which is what ties the tasks together and defines the actual structure of the DAG.
    - Task dependencies are primarily defined with the >> (downstream) and << (upstream) control flow operators.
    - Additional functions are available for more complex control flow definitions.
- A single Python script may contain multiple DAGs.

#### Running a DAG
- DAGs can be scheduled.
- There are 2 main ways to run DAGs:
    - triggering them manually via the web UI or via API;
    - scheduling them.
- When you trigger or schedule a DAG, a DAG instance is created, called a <strong>DAG run</strong>.
- DAG runs can run in <strong>parallel for the same DAG</strong> for separate data intervals.

#### Operators

- Operators are components that define what action each task performs.

- An Operator is conceptually a template for a predefined Task, that you can just define declaratively inside your DAG. ([Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html))

#### <i>ingest_script_local.py</i>
- in this project we are interested in downloading a csv file containing New York Taxi data hosted [here](https://github.com/DataTalksClub/nyc-tlc-data/releases/) (originally available on the [New York Taxi website](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page));
- the script imports the dataset as an iterator;
- it establishes a connection to the Postgres db and ingests the csv data into the database in chunks.

#### <i>data_ingestion_local.py</i>
- a dag file used by Airflow for workflow orchestration;

##### Main DAG Components and Setup
- the script is designed to run as an ETL pipeline;
- <code>LocalIngestionDag</code> automates the process of downloading a dataset file and ingesting it into a PostgreSQL database:
    - DAG Configuration:
        - <code>start_date</code>: specifies when the DAG can start. In this initial set up for using Airflow locally, we aim to upload data from a single csv file. We therefore setting up the start date to yesterday* ensuring it's close to the current time without triggering historical runs.

            \* I've tested setting the start date to <i>today</i> but the DAG was not triggered properly. The reason for this is in Airflow's scheduling behavior: when it sees the start date set to yesterday, the DAGs start straight away as Airflow sees it as a scheduled run that was missed and needs to catch up even with the catchup param set to False. If the start date is set to today, Airflow sees the DAG run's scheduled interval as still in process, and will not trigger DAG straight away. This DAG will only trigger on the next interval. This delay can make it seem like the DAG isn't running. 
        - <code>schedule_interval</code>: no recurring schedule for a one-time run
        - <code>catchup=False</code>: disables backfilling, which would otherwise run the DAG for every interval since the start_date. As our start date is set to yesterday we do not require backfilling.
- the script sets constants for the file to be downloaded - a compressed CSV file (*.csv.gz), representing NYC taxi data

##### DAG Tasks and Workflow
- two tasks specified in the script:
    1. wget_task - data extraction
        - downloads the csv file into the home directory within the container that is running the scheduler; the downloaded file is then passed as an input into the ingest_task.
        - uses BashOperator* to download the CSV file from the URL (URL_TEMPLATE) to the specified output directory (OUTPUT_FILE_TEMPLATE).
        
            <i>\* BashOperator is useful for executing shell commands in Airflow.</i>
    2. ingest_task - data loading
        - the <i>ingest_script_local.py</i> script is imported into the <i>data_ingestion_local.py</i> dag to be used as a callable function within the ingest_task.
        - PythonOperator is used in this DAG to call Python function ingest_callable directly within Airflow tasks.

##### Task Dependency
- The DAG’s task dependency is defined at the end with wget_task >> ingest_task, which ensures that ingest_task only runs after wget_task completes successfully.
- This dependency reflects a common ETL pipeline pattern where data extraction occurs before ingestion/loading.

##### DAG Run Results:

Two green squares indicates a successful run. This will take a few minutes to complete, until then you will see the squares in the "running" state.


<img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/2_workflow_orchestration/airflow_local/_doc/successeful_dag_run.png" alt="DAG run result in Airflow" width="600"/>

The yellow_taxi table should be created and accessible even if the dag is still running:
<img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/2_workflow_orchestration/airflow_local/_doc/ingested_data_in_postgres.png" alt="Data added to local Postgres db via Airflow" width="600"/>




### Credits & Further Reading:
- [Run Airflow via Docker on local machine using LocalExecutor](https://github.com/apuhegde/Airflow-LocalExecutor-In-Docker) by Apurva Hegde

- [Alvaro Navas' notes](https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/2_data_ingestion.md#creating-a-dag)

- [Ingesting Data to Local Postgres with Airflow](https://www.youtube.com/watch?v=s2U8MWJH5xA&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb) by DataTalkClub

- [DE_Zoomcamp_week_2_data_ingestion
/airflow/](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/4ecddc7ed8264b694136de2a6e84ce6f88401695/cohorts/2022/week_2_data_ingestion/airflow)

- [Airflow documentation on ways to create DAGs](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html)


 <!-- GCP: https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/4ecddc7ed8264b694136de2a6e84ce6f88401695/cohorts/2022/week_2_data_ingestion/airflow/dags/data_ingestion_gcs_dag.py -->
<!-- 
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
    - this is also created User with role Admin 
3. <b>Run Airflow</b>
    ```bash
    docker compose up -d
    ```
4. Access the Airflow GUI by browsing to localhost:8080.
    - Username and password are both airflow by default.


## Ingesting Data to Local Postgres with Airflow
### Tasks:
- Run our Postgres setup (module 1) locally along with the Airflow container.
- Use the ingest_data.py script (module 1) from a DAG to ingest the NYC taxi trip data to local Postgres.

#### Airflow Container
1. <strong>Prepare Ingestion Script.</strong>
    - use code from ingest_data.py;
    - wrap code inside ingest_callable();
    - the script receives now params from Airflow to connect to the local DB (ingest_script.py);
    - dockerize the script again with PythonOperator in our DAG (data_ingestion_local.py).
    
2. <strong>Prepare a DAG.</strong>

    The DAG will have the following tasks:
    1. A download BashOperator task: downloads the NYC taxi data.
    2. A PythonOperator task: calls ingest script to populate local database.
    3. Environment variables to connect to the local DB to be read from .env .

- The dependencies specified in for the Airflow container should include those needed for the ingest_script.py file.

- Build/Rebuild the Airflow image and start the Airflow container:
    ```bash
    docker compose build
    docker compose up airflow-init
    docker compose up
    ```
#### Local Postgres Container
- On a separate terminal find out which virtual network it's running on (most likely <i>airflow_default</i>):
    ```bash
    docker network ls
    ``` 
- Modify the docker-compose.yaml file from module 1 by adding the network info and commenting away the pgAdmin service in order to reduce the amount of resources we will consume. 

- Run the updated docker-compose-module2.yaml:
    ```bash
    docker compose -f docker-compose-module2.yaml up
    ```
    We need to explicitly call the file because we're using a non-standard name.
 -->








</br>
</hr>

## Issues Encountered

1. Could not connect to the local Postgres DB

Solution:
```bash
ps -ef | grep psql
ps -ef | grep postgres
less /etc/postgresql/15/main/postgresql.conf 
netstat
sudo apt install net-tools
netstat -tulpn 
sudo netstat -tulpn 
sudo systemctl start postgresql
sudo netstat -tulpn 
```

## Learning Materials Used

[Data Ingestion](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/cohorts/2022/week_2_data_ingestion)
[Introduction to Workflow Orchestration](https://www.youtube.com/watch?v=0yK7LXwYeD0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=18) (video)

[Setup Airflow Environment with Docker-Compose](https://www.youtube.com/watch?v=lqDMzReAtrw&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=19) (video)

[Local Setup for Airflow](https://www.youtube.com/watch?v=A1p5LQ0zzaQ) (video)

[Ingesting Data to Local Postgres with Airflow](https://www.youtube.com/watch?v=s2U8MWJH5xA) (video)

[Alvaro Navas's Course Notes](https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/2_data_ingestion.md#data-ingestion)
