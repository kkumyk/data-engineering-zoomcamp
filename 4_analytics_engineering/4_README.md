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
      - [Setting Up dbt Cloud](#setting-up-dbt-cloud)
      - [Starting a dbt Project](#starting-a-dbt-project)
    - [Developing taxi\_rides\_ny dbt Project](#developing-taxi_rides_ny-dbt-project)
    - [Deploying With dbt](#deploying-with-dbt)
      - [Anatomy of a dbt Model](#anatomy-of-a-dbt-model)
      - [Types of Materialization Strategies](#types-of-materialization-strategies)


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
1. a development dataset, e.g.: dbt_dev
2. a production dataset, e.g.: dbt_prod
   
#### Setting Up dbt Cloud
1. Got to the dbt homepage and [sign up](https://www.getdbt.com/signup) to create a user account.
2. Set up a GitHub repo for your project.
3. Connect dbt to BigQuery development dataset and to the Github repo by following [these instructions](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/04-analytics-engineering/dbt_cloud_setup.md).
   
#### Starting a dbt Project
1. In the IDE windows, press the green Initilize button to create the project files.
2. Inside dbt_project.yml, change the project name both in the name field as well as right below the models: block. You may comment or delete the example block at the end.


### Developing taxi_rides_ny dbt Project
1. After setting up dbt Cloud account, in the Settings of your project rename the default name to "taxi_rides_ny".
2. Reference the given name in the dbt_project.yml file under the "name:" and straight after the "models:" line:
   ```yml
    name: 'taxi_rides_ny'   

    models:
      taxi_rides_ny:
   ```
3. Under the model folder create two folders: code and staging.
4. In the staging folder create two files:
   - schema.yml, here define:
     - the database the data will be coming from
     - the schema
     - the (source) tables
     ```yml
      version: 2

      sources:
          - name: staging
            database:  your-BigQuery-dataset-name
            schema: trips_data_all

            tables:
                - name: green_tripdata_external_table
                - name: yellow_tripdata_external_table
      ```
    - stg_green_tripdata.sql will contain:
      ```yml
      {{ config(materialized='view') }}

      select * from {{ source('staging', 'green_tripdata_external_table') }}
      limit 100
      ```
      The query will create a view in the staging dataset/schema in our database under the development dataset:

      <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/stg_green_tripdata_view.png" alt="staging green trip data view" width="300"/>

      We make use of the source() function to access the green taxi data table, which is defined inside the schema.yml file.
5.  Build your project.
6.  Define a get_payment_type_description macro under the macros folder.
    ```sql
    --- get_payment_type_description.sql

    {# This macro returns the description of the payment_type #}

    {% macro get_payment_type_description(payment_type) %}

        case {{ payment_type }}
            when 1 then 'Credit card'
            when 2 then 'Cash'
            when 3 then 'No charge'
            when 4 then 'Dispute'
            when 5 then 'Unknown'
            when 6 then 'Voided trip'
        end
        
    {% endmacro %}
    ```
7. Use the above macro in the stg_green_tripdata.sql by replacing its contents with:
   ```sql
    select
        {{ get_payment_type_description('payment_type') }} as payment_type_description,
        congestion_surcharge
    from {{ source('staging','green_tripdata_external_table') }}
    where vendorid is not null
   ```
   After the project is built, the stg_trip_data view will be updated with the data below:
  

    <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/payment_model_bq_results.png" alt="payment model bq results" width="600"/>








### Deploying With dbt
[video source 4.3.1](https://www.youtube.com/watch?v=UVI30Vxzd6c&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=40)

#### Anatomy of a dbt Model

- dbt models are mostly written in SQL (remember that a dbt model is essentially a SELECT query)
- the config() function is commonly used at the beginning of a model to define a materialization strategy - a strategy for persisting dbt models in a warehouse. 

Here's an example dbt model:
```sql
{{
    config(materialized='table')
}}

SELECT *
FROM staging.source_table
WHERE record_state = 'ACTIVE'
```
#### [Types of Materialization Strategies](https://docs.getdbt.com/docs/build/materializations)
Materializations are strategies for persisting dbt models in a warehouse.

Types of materializations built into dbt:
1. table - the model will be rebuilt as a table on each run
2. view - the model will be rebuild on each run as a SQL view
3. incremental - a table strategy that allows to add/update records incrementally rather than rebuilding the complete table on each run
4. ephemeral - creates a Common Table Expression (CTE)
5. materialized view
6. [custom materializations](https://docs.getdbt.com/guides/create-new-materializations?step=1) for advanced users.
   
The above model will be compiled by dbt into the following SQL query:
```sql
CREATE TABLE my_schema.my_model AS (
    SELECT *
    FROM staging.source_table
    WHERE record_state = 'ACTIVE'
)
```
After the code is compiled, dbt will run the compiled code in the Data Warehouse.
