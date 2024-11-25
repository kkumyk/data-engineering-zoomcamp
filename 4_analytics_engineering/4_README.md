- [Analytics Engineering](#analytics-engineering)
  - [Prerequisites](#prerequisites)
  - [What is Analytics Engineering?](#what-is-analytics-engineering)
  - [Data Modeling Concepts](#data-modeling-concepts)
    - [ETL vs ELT](#etl-vs-elt)
    - [Dimensional Modeling](#dimensional-modeling)
  - [Introduction to dbt](#introduction-to-dbt)
    - [What is dbt?](#what-is-dbt)
    - [How does dbt work?](#how-does-dbt-work)
      - [What is a dbt model?](#what-is-a-dbt-model)
    - [How to use dbt?](#how-to-use-dbt)
    - [Setting Up dbt](#setting-up-dbt)


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

    <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/yellow_taxi_dnday, 27 January 2025a_three_workflows_failed.png" alt="DAG run result in Airflow for multiple files - three failed" width="600"/>

    I saw this as a good opportunity to test the [data_ingestion_gcs.py (uploads a single file to GCS)](https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/2_workflow_orchestration/airflow_gcp/dags/data_ingestion_gcs.py). I run this dag for the missing three files. They will first end in the GCS bucket on the same level as the taxi types folders, see below the uploaded file for May 2019:
    
    <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/yellow_2019_05_file_upload.png" alt="DAG run result - a single file upload to GCS bucket" width="600"/>

    Each file was then moved manually from the bucket to the corresponding taxi type/year folder in GCS. The next step is to move the data from these files into BigQuery.
    
    I've run the gcs_2_bq_dag.py DAG for the yellow taxi type only to start with (TAXI_TYPES = {'yellow': 'tpep_pickup_datetime'}) and created an external and a partitioned tables containing data fro 2019 and 2020:

    <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/gcs_to_bg_yellow_2019_2020.png" alt="DAG run result: yellow taxi type data ingested to the external and partitioned tables" width="600"/>
    
    This should be enough to play around in the module 4. All in one, it looks like the work done in the previous three modules was not in vein and I should have data required to continue with the material in the Analytics Engineering module of the course. :) 

## What is Analytics Engineering?
[video source 4.1.1](https://www.youtube.com/watch?v=uF76d5EmdtU&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=35)

Tools that shaped the ways of working with data:

1. MPP (Massively Parallel Processing) Databases 
   - Lower the cost of storage
   - BigQuery, Snowflake, Redshift

2. Data-Pipelines-As-A-Service
    - Simplify the ETL process
    - Fivetran, Stitch

3. SQL-first / Version Control Systems
    - Looker
4. Self Service Analytics
    - Mode
5. Data governance

Traditional role separation of data teams:

- data engineer prepares and maintains the data infrastructure
- data analyst uses data to answer questions and solve problems
- data scientist predicts the future based on pastData Modeling Concepts
Data engineers are good software engineers but they don't have the training in how the data is going to be used by the business users.

The analytics engineer fills the gap by introducing the good software engineering practices to the efforts of data analysts and data scientists.
  
The analytics engineer may be exposed to the following tools:
  - Data Loading (Stitch)
  - Data Storing (Data Warehouses)
  - Data Modeling (dbt, Dataform)
  - Data Presentation (BI tools like Looker, Mode, Tableau)

## Data Modeling Concepts

### ETL vs ELT
This part of the lesson covers the TRANSFORM part of ELT process.

### Dimensional Modeling

[Ralph Kimball's Dimensional Modeling](https://docs.getdbt.com/blog/kimball-dimensional-model) - an approach to Data Warehouse design focuses on:
1. Deliver data which is understandable to the business users.
2. Deliver fast query performance.
3. Reduce redundant data (prioritized by other approaches such as 3NF by Bill Inmon) - a secondary goal.
   
[Data Vaults](https://www.wikiwand.com/en/articles/Data_vault_modeling) - an alternative approach to Data Warehouse design.

## Introduction to dbt
[video source 4.1.2](https://www.youtube.com/watch?v=4eCouvVOJUw&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=36)

### What is dbt?
- data build tool
- a transformation tool
- allows us to transform/process raw data in our Data Warehouse
- allows us to introduce good software engineering practices by defining a <i>deployment workflow</i>:
  1. Develop models
  2. Test and document models
  3. Deploy models with version control and CI/CD

### How does dbt work?
- define a modeling layer that sits on top of our Data Warehouse
- the modeling layer will turn tables into models
- the defined models will be transformed into derived models and will be stored into the Data Warehouse for persistence

#### What is a dbt model?
- a .sql file with a SELECT statement
- no DDL or DML is used
- dbt will compile the file and run it in our Data Warehouse

### How to use dbt?

dbt's 2 main components:

1. dbt Core
    - open-source and free to use project that allows the data transformation
    - builds and runs a dbt project (.sql and .yaml files)
    - includes SQL compilation logic, macros and database adapters
    - includes a CLI interface to run dbt commands locally

2. dbt Cloud
    - SaaS application to develop and manage dbt projects
    - Web-based IDE to develop, run and test a dbt project
    - jobs orchestration
    - logging and alerting
    - intregrated documentation
    - free for individuals
  
For integration with BigQuery we will use the dbt Cloud IDE.

### Setting Up dbt
Before we begin, create 2 new empty datasets for your project in BigQuery:
1. a development dataset
2. a production dataset