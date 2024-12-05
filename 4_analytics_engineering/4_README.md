
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
        - [Calling the macro in our model](#calling-the-macro-in-our-model)
    - [Testing and Documenting the dbt Project](#testing-and-documenting-the-dbt-project)
      - [Documentation](#documentation)
    - [Deploying with dbt Cloud](#deploying-with-dbt-cloud)
  - [Data Visualisation with Looker Studio](#data-visualisation-with-looker-studio)
  - [Credits](#credits)


# Analytics Engineering

## Prerequisites

- a running warehouse (BigQuery or Postgres)
- a set of running pipelines ingesting the project dataset (week 3 completed)

    The following datasets ingested from the course [Datasets list](https://github.com/DataTalksClub/nyc-tlc-data/):
    - Yellow taxi data - Years 2019 and 2020
    - Green taxi data - Years 2019 and 2020
    - fhv data - Year 2019.

    <i>Note</i> that there are two ways available to load data files quicker directly to GCS, without Airflow: [option 1](https://www.youtube.com/watch?v=Mork172sK_c&list=PLaNLNpjZpzwgneiI-Gl8df8GCsPYp_6Bs) and [option 2](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse/extras) via [web_to_gcs.py script](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/03-data-warehouse/extras/web_to_gcs.py).

    However, if you've completed modules 1-3, the above data should be already be found in your BigQuery account.

    Starting with checking the file uploads done in the previous modules is a good exercise for reviewing of what was done in the previous three modules.

    The prerequisites in module 4 require the data for 2019 and 2020 as this module using Airflow for orchestration was done a couple of years ago. The FHV data for 2019 was requested for the homework completion. I decided to first focus on uploads for the Yellow and Green data as it looks like these will be used throughout the module.

    To upload these files I run the [data_ingestion_gcs_multiFile.py dag](https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/2_workflow_orchestration/airflow_gcp/dags/data_ingestion_gcs_multiFile.py) from the airflow_gcp folder by first adjusting the start and the end dates and commenting out the tasks focusing on fhv file uploads. The result was that all files apart from the three months's data in 2019 for the Yellow taxi type were not uploaded, see below: 

    <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/yellow_taxi_data_three_workflows_failed.png" alt="DAG run result in Airflow for multiple files - three failed" width="600"/>

    I saw this as a good opportunity to test the [data_ingestion_gcs.py (uploads a single file to GCS)](https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/2_workflow_orchestration/airflow_gcp/dags/data_ingestion_gcs.py). I run this dag for the missing three files. They will first end in the GCS bucket on the same level as the taxi types folders, see below the uploaded file for May 2019:
    
    <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/yellow_2019_05_file_upload.png" alt="DAG run result - a single file upload to GCS bucket" width="600"/>

    Each file was then moved manually from the bucket to the corresponding taxi type/year folder in GCS. The next step is to move the data from these files into BigQuery.
    
    I've run the gcs_2_bq_dag.py DAG for the yellow taxi type only to start with (TAXI_TYPES = {'yellow': 'tpep_pickup_datetime'}) and created an external and a partitioned tables containing data fro 2019 and 2020:

    <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/gcs_to_bg_yellow_2019_2020.png" alt="DAG run result: yellow taxi type data ingested to the external and partitioned tables" width="1100"/>
    
    This should be enough to play around in the module 4. All in one, it looks like the work done in the previous three modules was not in vein and I should have data required to continue with the material in the Analytics Engineering module of the course. :) 

## What is Analytics Engineering?
[video source 4.1.1](https://www.youtube.com/watch?v=uF76d5EmdtU&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=35)

Tools that shaped the ways of working with data:

MPP (Massively Parallel Processing) Databases

   - Lower the cost of storage
   - BigQuery, Snowflake, Redshift

Data-Pipelines-As-A-Service

- Simplify the ETL process
- Fivetran, Stitch

SQL-first / Version Control Systems
    - Looker
Self Service Analytics
    - Mode
Data governance

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

  ##### Calling the macro in our model
  Let's update the model by adding more data fields. Note that we are calling the payment description type macro with <code>{{ get_payment_type_description("payment_type") }} as payment_type_description,</code> line. See below:

  ```sql
  {{ config( materialized='view')}}

  select
      -- identifiers,
      VendorId as vendorid,
      RatecodeID as ratecodeid,
      PULocationID as pickup_locationid,
      DOLocationID as dropoff_locationid,
      
      -- timestamps
      lpep_pickup_datetime as pickup_datetime,
      lpep_dropoff_datetime as dropoff_datetime,
      
      -- trip info
      store_and_fwd_flag,
      passenger_count as passenger_count,
      trip_distance as trip_distance,
      trip_type as trip_type,

      -- payment info
      fare_amount,
      extra,
      mta_tax,
      tip_amount,
      tolls_amount,
      ehail_fee,
      improvement_surcharge,
      total_amount,
      payment_type,
      {{ get_payment_type_description("payment_type") }} as payment_type_description,
      congestion_surcharge
      
  from {{ source('staging','green_tripdata_external_table') }}
  limit 100
  ``` 

  Note that above query the macro has been turned into code and also our FROM statement has got the complete path:

  ```sql
  select
    -- identifiers,
    VendorId as vendorid,
    RatecodeID as ratecodeid,
    PULocationID as pickup_locationid,
    DOLocationID as dropoff_locationid,
    
    -- timestamps
    lpep_pickup_datetime as pickup_datetime,
    lpep_dropoff_datetime as dropoff_datetime,
    
    -- trip info
    store_and_fwd_flag,
    passenger_count as passenger_count,
    trip_distance as trip_distance,
    trip_type as trip_type,

    -- payment info
    fare_amount,
    extra,
    mta_tax,
    tip_amount,
    tolls_amount,
    ehail_fee,
    improvement_surcharge,
    total_amount,
    payment_type,
    

    case payment_type
        when 1 then 'Credit card'
        when 2 then 'Cash'
        when 3 then 'No charge'
        when 4 then 'Dispute'
        when 5 then 'Unknown'
        when 6 then 'Voided trip'
    end
    
 as payment_type_description,
    congestion_surcharge
    
from `dtc-de-course-YOUR_DATASET_ID`.`trips_data_all`.`green_tripdata_external_table`
limit 100
```
And the updated BigQuery view will look like:

  <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/stg_green_tripdata_with_payment_description.png" alt="payment model bq results" width="1100"/>


- We can use Macros in a single project but we can also use them across projects with packages.
- These are like libraries in programming languages.

8. We are now going to install a package:
- Install [dbt_utils](https://hub.getdbt.com/dbt-labs/dbt_utils/latest/) package by adding packages.yml file at the top level of your dbt project and adding the content below to the file:

  ```yml
  packages:
    - package: dbt-labs/dbt_utils
      version: 1.3.0
  ```
- Save the file and install the package by running the <code>dbt deps</code> command. 
- After this we see a dbt_packages folder with a dbt_utils folder and a collection of macros in our dbt project:
  <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/dbt_packages_install_results.png" alt="dbt packages install results" width="300"/>


9. Adding the Identifiers
    - We are going to use our dbt_utils package to create a unique id ‘tripid’.
    - In our stg_green_tripdata.sql model we will add this line:
      
      ```sql
      select
      -- identifiers,
      VendorId as vendorid,
      {{ dbt_utils.generate_surrogate_key(['VendorId', 'lpep_pickup_datetime']) }} as tripid, 
      ...
      ```
     - Save and run this model.
     - Refresh your green data staging view in BigQuery to see it the updated with the unique identifier:
  
        <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/tripid_unique_identifier_in_bq_results.png" alt="tripid unique identifier in bq results" width="500"/>

10. Variables

- Variables are values that we can use across the project.
- We can do this in one of two ways:
  - in the dbt_project.yml file:

    ```yml
    vars:
      is_test_run: false
    ```

  - on the command line
- We need to change our model to cater for this by adding the code below to our model which will either limit the results or not limit them depending on what we type on the command line during a run:
  ```sql
  --- stg_green_data.sql
  ...
    from {{ source('staging','green_tripdata_external_table') }}

  -- dbt build --select <model_name> --vars '{'is_test_run': 'false'}'

  {% if var('is_test_run', default=true) %}

    limit 23

  {% endif %}
  ```
- The compiled code takes the default value and will limit the results in the staging view:
  ```sql
  --- stg_green_data.sql
  ...
  from `dtc-de-course-YOUR_DATASET_ID`.`trips_data_all`.`green_tripdata_external_table`

  -- dbt build --select <model_name> --var '{'is_test_run': 'false'}'

    limit 23
  ```
 - Add <code>vars: is_test_run: false</code> as shown above to the dbt_project.yml file.
 - Run the project again and review the compiled file. You should see that <code>limit</code> does not appear in the compiled code meaning that it will not be applied to the view.

11.  Comparing the BigQuery Schemas for the Green and Yellow Tables:
      - I compared the field names for the green and yellow tables and saw that the green table has two more fields that the yellow does not: <i>ehail_fee</i> and <i>trip_type</i>. I understood from the tutorial that the called fields should be the same from both tables.
       - Adjusting green trip data model:
         - I’m going to go back to my green trip dbt model and change it so that it’s not importing these two fields by removing them from the stg_green_tripdata.sql model. I re-build the project and check the returned results in the BigQuery.
       - I also wanted to look into the issue I had with partitioning the green data external table. I managed to create a partitioned table for the yellow one, but the same did not work for the green table due to the following error <code>Parquet column 'ehail_fee' has type DOUBLE which does not match the target cpp_type INT64.</code> The data I see for this column is simply <i>null</i> and does not match the schema defined for this field being set to INTEGER. On the UI I simply don't see how to edit the schema and hence I still cannot create the partitioned table for the green taxi data set.
       - Next, duplicate the stg_green_data.sql dbt model, then:
         - replace the "green" to yellow in the file name
         - change the lpep_pickup_datetime, lpep_dropoff_datetime to tpep_pickup_datetime, tpep_dropoff_datetime; do the same in the <code>{{ dbt_utils.generate_surrogate_key(['VendorId', 'tpep_pickup_datetime']) }} as tripid,</code>
         - adjust the source name in the FROM statement: <code>from {{ source('staging','yellow_tripdata') }}</code>
  
You should now have two BigQuery views with the same schema with the new view stg_yellow_tripdata been created.

12. Seed File Creation
    After running our seed file, a new taxi zone lookup table is created in BigQuery.
    To complete this step, I've followed [instructions found here](https://learningdataengineering540969211.wordpress.com/2022/02/20/week-4-de-zoomcamp-4-3-1-build-the-first-dbt-models-part-6-seeds/).
13. Seed Based dbt Model Creation: dim_zones model
    - create a new model in the Core folder: dim_zones.sql. Note that here instead of creating a view we create a table now. Add the snippet below to the file:
    ```sql
    {{ config(materialized='table') }}

    select 
        locationid, 
        borough, 
        zone, 
        replace(service_zone,'Boro','Green') as service_zone 
    from {{ ref('taxi_zone_lookup') }}
    ```
    - Note that in the above file we replace ‘Green’ with ‘Boro’ in the service_zone field. This is because we want it to be consistent with service_zone ‘Yellow’ naming convention. 
14. Creating a third model - <code>fact_trips.sql</code> model - the second on our Core file
    - This model is referencing both staging models: <code>stg_green_tripdata</code> and <code>stg_yellow_tripdata</code>.
    - I had to remove to field in step 11 which will not be included in this model as a result of it.
    ```sql
    {{
        config(
            materialized='table'
        )
    }}

    with green_tripdata as (
        select *, 
            'Green' as service_type
        from {{ ref('stg_green_tripdata') }}
    ), 
    yellow_tripdata as (
        select *, 
            'Yellow' as service_type
        from {{ ref('stg_yellow_tripdata') }}
    ), 
    trips_unioned as (
        select * from green_tripdata
        union all 
        select * from yellow_tripdata
    ), 
    dim_zones as (
        select * from {{ ref('dim_zones') }}
        where borough != 'Unknown'
    )
    select trips_unioned.tripid, 
        trips_unioned.vendorid, 
        trips_unioned.service_type,
        trips_unioned.ratecodeid, 
        trips_unioned.pickup_locationid, 
        pickup_zone.borough as pickup_borough, 
        pickup_zone.zone as pickup_zone, 
        trips_unioned.dropoff_locationid,
        dropoff_zone.borough as dropoff_borough, 
        dropoff_zone.zone as dropoff_zone,  
        trips_unioned.pickup_datetime, 
        trips_unioned.dropoff_datetime, 
        trips_unioned.store_and_fwd_flag, 
        trips_unioned.passenger_count, 
        trips_unioned.trip_distance, 
        <!-- trips_unioned.trip_type,  -->
        trips_unioned.fare_amount, 
        trips_unioned.extra, 
        trips_unioned.mta_tax, 
        trips_unioned.tip_amount, 
        trips_unioned.tolls_amount, 
        <!-- trips_unioned.ehail_fee,  -->
        trips_unioned.improvement_surcharge, 
        trips_unioned.total_amount, 
        trips_unioned.payment_type, 
        trips_unioned.payment_type_description
    from trips_unioned
    inner join dim_zones as pickup_zone
    on trips_unioned.pickup_locationid = pickup_zone.locationid
    inner join dim_zones as dropoff_zone
    on trips_unioned.dropoff_locationid = dropoff_zone.locationid
    ```
  The whole point of creating the fact_trips model is to show that we can take both existing models – the staging green trip data and the staging yellow trip data. 


  <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/fact_trips_mdl.png" alt="fact trips dbt model" width="1000"/>

  - After running the model I hit a weired error : <code> Access Denied: BigQuery BigQuery: Permission denied while globbing file pattern. dbt-service-account@dtc-de-....iam.gserviceaccount.com does not have storage.objects.list access to the Google Cloud Storage bucket. Permission 'storage.objects.list' denied on resource (or it may not exist). Please make sure gs://dtc_data_lake_dtc-de-.../raw/green_tripdata/* is accessible via appropriate IAM roles, e.g. Storage Object Viewer or Storage Object Creator</code>
  - I see that [a similar permission error was also encountered](https://learningdataengineering540969211.wordpress.com/2022/02/20/week-4-de-zoomcamp-4-3-1-build-the-first-dbt-models-part-6-seeds/) by prople from previous cohorts. As in these notes, after reviewing the permissions for the service account at first, I simple re-run the model and ... miracle of the miracles... it simply worked. At this stage, going into the reasons for why this error did appear and then simply resolved by itself is something outside I can afford based on my time budget. My estimate of where I in the module's material is something about 60% - I hope - and I simply will carry one with the next step.
  - the result of running the fact_trips.sql model is a <code>dim_zones</code> table in your BigQuery's dev environtment dataset.

### Testing and Documenting the dbt Project

1. Create dm_monthly_zone_revenue.sql file in the <code>core</code> folder of the dbt project and add the content below to it:
```sql
{{ config(materialized='table') }}

with trips_data as (
    select * from {{ ref('fact_trips') }}
)
    select 
    -- Reveneue grouping 
    pickup_zone as revenue_zone,
    -- {{ dbt.date_trunc("month", "pickup_datetime") }} as revenue_month, 
    date_trunc(pickup_datetime, month) as revenue_month,

    service_type, 

    -- Revenue calculation 
    sum(fare_amount) as revenue_monthly_fare,
    sum(extra) as revenue_monthly_extra,
    sum(mta_tax) as revenue_monthly_mta_tax,
    sum(tip_amount) as revenue_monthly_tip_amount,
    sum(tolls_amount) as revenue_monthly_tolls_amount,
    sum(improvement_surcharge) as revenue_monthly_improvement_surcharge,
    sum(total_amount) as revenue_monthly_total_amount,

    -- Additional calculations
    count(tripid) as total_monthly_trips,
    avg(passenger_count) as avg_monthly_passenger_count,
    avg(trip_distance) as avg_monthly_trip_distance

    from trips_data
    group by 1,2,3
```
Note that I again removed the two fields as per step 11.

2. We now need to update our schema.yml from the staging folder by adding models section to it. The models part will be added from the [course's repo](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/04-analytics-engineering/taxi_rides_ny/models/staging/schema.yml#L17). Note that the result of putting these adjustments in is to both document and test our models. 

3. Tests
- A test is an assumption that we make about our data. In dbt a test is the same as a model – it is a SELECT query. What a test does in dbt is report on how many records do not follow the assumption that we made.
- dbt provides us with four basic tests that we can add to our columns to check.
- Note that we use a variable in the added schema and that’s because our accepted values are going to apply to both our green and yellow trip data. We therefore need to define this variable in the <code>project.yml</code> file.
- Adjust the staging models as per "Fix green/yellow trip data" sections [here](https://learningdataengineering540969211.wordpress.com/2022/02/20/week-4-de-zoomcamp-4-3-2-testing-and-documenting-the-project-part-1/).
- Running the <code>dbt test</code> confirms that the permissions error still persists. Only after adding "Storage Object Creator" as a role to the dbt-service-account the issue is resolved, the tests are passed with only two warnings:
  <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/dbt_test_results.png" alt="dbt test results" width="1100"/>

- Let's re-build the whole project to see if it works as a whole. I run, and the build is successeful with no test errors logged.
  
  <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/dbt_build_run_result.png" alt="dbt build run result" width="1100"/>


#### Documentation

- dbt provides a way to generate documentation for the whole project.
- We can render this as a website as well.
- There is one thing that we are missing in terms of our documentation up to this stage and that is the schema.yml for the Core folder.
- Let’s create that file now. Copy its contents from the [course's repo](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/04-analytics-engineering/taxi_rides_ny/models/core/schema.yml).
- I've again removed the ehail and trip_types fields from this schema file and re-buid the whole project to make sure all works as expected. All 17 tests have passed and I'm happy to move one to the deployment part of this project.

Before doing this, let's have a look at what was acheaved by completing this part of the module in BigQuery. We see that we have created four tables and two views in our development dataset:
  <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/dev_env_bq_result.png" alt="dev_env_bq_result" width="600"/>

### Deploying with dbt Cloud
After testing and documenting our dbt project, it's time to deploy it. Note that:
- out development environtment is separate from our production environtment;
- deployment will be done via version control and CI/CD (Continuous Integration and Continuous Delivery).
- before continue, make sure everything that was previously done is commited to the main branch of your GitHub repo.
- navigate to your dbt environments via Deploy > Environments
- at this stage only Development environment should be should there
- create a Production environtment: click on the "Create environtment" button on the top right
- field that need to be added/selected are:
  - Environment name: Production
  - Environment type: Deployment
  - Connection: BigQuery
  - Dataset: the name of your production dataset in BigQuery 
- go to Deploy > Jobs
- click on the "Create job" button, add the following details:
  - Job name: dbt_build
  - Environment: Production
  - Execution settings > Commands: 
    - dbt seed
    - dbt run
    - dbt test
  - there is of course options to schedule the job which I'm not using now as I want manually run the job to see if it simply works in the first place; I therefore save the job and run it by clicking on the "Run now" button;
- after the job has run and marked as "succeeded" we can see the production dataset being updated in the BigQuery:
  <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/dev_prod_bq.png" alt="Production run results in BigQuery succeeded" width="600"/>


## [Data Visualisation with Looker Studio](https://learningdataengineering540969211.wordpress.com/2022/02/20/week-4-de-zoomcamp-4-5-1-visualising-the-data-with-google-data-studio-part-1/)

- go to [Looker Studo](https://lookerstudio.google.com/navigation/reporting)
- create a data source
- select BigQuery from Google Connectors
- under displayed projects select a table from your production dataset
- create a report
- add sparkline chart to your new report
- select the fields as on the screenshot below:
<img src="https://learningdataengineering540969211.wordpress.com/wp-content/uploads/2022/02/screenshot-from-2022-02-20-14-56-44.png?w=1024" alt="dev_env_bq_result" width="1000"/>
- add a control for the date (Add a control > Date Range Control > ) range by selecting the data range from the 1st of Jan 2019 to 31st of December of 2020.
  
- If all went well, you will see the graph updated to the below:
<img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/fact_trips_2019_2020_data.png" alt="dev_env_bq_result" width="1000"/>

- adding more charts by following [notes here](https://learningdataengineering540969211.wordpress.com/2022/02/21/week-4-de-zoomcamp-4-5-1-visualising-the-data-with-google-data-studio-part-2/)




## Credits
- [Notes by Alvaro Navas](https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/4_analytics.md)
- [Sandy's DE learning blog](https://learningdataengineering540969211.wordpress.com/2022/02/17/week-4-setting-up-dbt-cloud-with-bigquery/)



























<!-- ### Anatomy of a dbt Model

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

#### Packages
- Macros can be exported to packages, similarly to how classes and functions can be exported to libraries.
- Packages contain standalone dbt projects with models and macros that tackle a specific problem area.
- To use a package, you must first create a packages.yml file in the root of your work directory. E.g.:
  ```yml
  packages:
    - package: dbt-labs/dbt_utils
      version: 1.3.0
  ```
- After declaring your packages, you need to install them by running the <code>dbt deps</code> command.




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

#### Packages
- Macros can be exported to packages, similarly to how classes and functions can be exported to libraries.
- Packages contain standalone dbt projects with models and macros that tackle a specific problem area.
- To use a package, you must first create a packages.yml file in the root of your work directory. E.g.:
  ```yml
  packages:
    - package: dbt-labs/dbt_utils
      version: 1.3.0
  ```
- After declaring your packages, you need to install them by running the <code>dbt deps</code> command. -->



<!-- # Analytics Engineering

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
2. Inside dbt_project.yml, change the project name both in the name field as well as right below the models: block. You may comment or delete the example block at the end. -->

<!-- 
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

  ##### Calling the macro in our model
  Let's update the model by adding more data fields. Note that we are calling the payment description type macro with <code>{{ get_payment_type_description("payment_type") }} as payment_type_description,</code> line. See below:

  ```sql
  {{ config( materialized='view')}}

  select
      -- identifiers,
      VendorId as vendorid,
      RatecodeID as ratecodeid,
      PULocationID as pickup_locationid,
      DOLocationID as dropoff_locationid,
      
      -- timestamps
      lpep_pickup_datetime as pickup_datetime,
      lpep_dropoff_datetime as dropoff_datetime,
      
      -- trip info
      store_and_fwd_flag,
      passenger_count as passenger_count,
      trip_distance as trip_distance,
      trip_type as trip_type,

      -- payment info
      fare_amount,
      extra,
      mta_tax,
      tip_amount,
      tolls_amount,
      ehail_fee,
      improvement_surcharge,
      total_amount,
      payment_type,
      {{ get_payment_type_description("payment_type") }} as payment_type_description,
      congestion_surcharge
      
  from {{ source('staging','green_tripdata_external_table') }}
  limit 100
  ``` 

  Note that above query the macro has been turned into code and also our FROM statement has got the complete path:

  ```sql
  select
    -- identifiers,
    VendorId as vendorid,
    RatecodeID as ratecodeid,
    PULocationID as pickup_locationid,
    DOLocationID as dropoff_locationid,
    
    -- timestamps
    lpep_pickup_datetime as pickup_datetime,
    lpep_dropoff_datetime as dropoff_datetime,
    
    -- trip info
    store_and_fwd_flag,
    passenger_count as passenger_count,
    trip_distance as trip_distance,
    trip_type as trip_type,

    -- payment info
    fare_amount,
    extra,
    mta_tax,
    tip_amount,
    tolls_amount,
    ehail_fee,
    improvement_surcharge,
    total_amount,
    payment_type,
    

    case payment_type
        when 1 then 'Credit card'
        when 2 then 'Cash'
        when 3 then 'No charge'
        when 4 then 'Dispute'
        when 5 then 'Unknown'
        when 6 then 'Voided trip'
    end
    
 as payment_type_description,
    congestion_surcharge
    
from `dtc-de-course-YOUR_DATASET_ID`.`trips_data_all`.`green_tripdata_external_table`
limit 100
```
And the updated BigQuery view will look like:

  <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/stg_green_tripdata_with_payment_description.png" alt="payment model bq results" width="1100"/>


- We can use Macros in a single project but we can also use them across projects with packages.
- These are like libraries in programming languages.

8. We are now going to install a package:
- Install [dbt_utils](https://hub.getdbt.com/dbt-labs/dbt_utils/latest/) package by adding packages.yml file at the top level of your dbt project and adding the content below to the file:

  ```yml
  packages:
    - package: dbt-labs/dbt_utils
      version: 1.3.0
  ```
- Save the file and install the package by running the <code>dbt deps</code> command. 
- After this we see a dbt_packages folder with a dbt_utils folder and a collection of macros in our dbt project:
  <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/dbt_packages_install_results.png" alt="dbt packages install results" width="500"/>


9. Adding the Identifiers
    - We are going to use our dbt_utils package to create a unique id ‘tripid’.
    - In our stg_green_tripdata.sql model we will add this line:
      
      ```sql
      select
      -- identifiers,
      VendorId as vendorid,
      {{ dbt_utils.generate_surrogate_key(['VendorId', 'lpep_pickup_datetime']) }} as tripid, 
      ...
      ```
     - Save and run this model.
     - Refresh your green data staging view in BigQuery to see it the updated with the unique identifier:
  
        <img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/4_analytics_engineering/_doc/tripid_unique_identifier_in_bq_results.png" alt="tripid unique identifier in bq results" width="500"/>

10. Variables

- Variables are values that we can use across the project.
- We can do this in one of two ways:
  - in the dbt_project.yml file:

    ```yml
    vars:
      is_test_run: false
    ```

  - on the command line
- We need to change our model to cater for this by adding the code below to our model which will either limit the results or not limit them depending on what we type on the command line during a run:
  ```sql
  --- stg_green_data.sql
  ...
    from {{ source('staging','green_tripdata_external_table') }}

  -- dbt build --select <model_name> --vars '{'is_test_run': 'false'}'

  {% if var('is_test_run', default=true) %}

    limit 23

  {% endif %}
  ```
- The compiled code takes the default value and will limit the results in the staging view:
  ```sql
  --- stg_green_data.sql
  ...
  from `dtc-de-course-YOUR_DATASET_ID`.`trips_data_all`.`green_tripdata_external_table`

  -- dbt build --select <model_name> --var '{'is_test_run': 'false'}'

    limit 23
  ```
 - Add <code>vars: is_test_run: false</code> as shown above to the dbt_project.yml file.
 - Run the project again and review the compiled file. You should see that <code>limit</code> does not appear in the compiled code meaning that it will not be applied to the view.

11.  Comparing the BigQuery Schemas for the Green and Yellow Tables:
      - I compared the field names for the green and yellow tables and saw that the green table has two more fields that the yellow does not: <i>ehail_fee</i> and <i>trip_type</i>. I understood from the tutorial that the called fields should be the same from both tables.
       - Adjusting green trip data model:
         - I’m going to go back to my green trip dbt model and change it so that it’s not importing these two fields by removing them from the stg_green_tripdata.sql model. I re-build the project and check the returned results in the BigQuery.
       - I also wanted to look into the issue I had with partitioning the green data external table. I managed to create a partitioned table for the yellow one, but the same did not work for the green table due to the following error <code>Parquet column 'ehail_fee' has type DOUBLE which does not match the target cpp_type INT64.</code> The data I see for this column is simply <i>null</i> and does not match the schema defined for this field being set to INTEGER. On the UI I simply don't see how to edit the schema and hence I still cannot create the partitioned table for the green taxi data set.
       - Next, duplicate the stg_green_data.sql dbt model, then:
         - replace the "green" to yellow in the file name
         - change the lpep_pickup_datetime, lpep_dropoff_datetime to tpep_pickup_datetime, tpep_dropoff_datetime; do the same in the <code>{{ dbt_utils.generate_surrogate_key(['VendorId', 'tpep_pickup_datetime']) }} as tripid,</code>
         - adjust the source name in the FROM statement: <code>from {{ source('staging','yellow_tripdata') }}</code>
  
You should now have two BigQuery views with the same schema with the new view stg_yellow_tripdata been created.

12. Seed File Creation
    After running our seed file, a new taxi zone lookup table is created in BigQuery.
    To complete this step, I've followed [instructions found here](https://learningdataengineering540969211.wordpress.com/2022/02/20/week-4-de-zoomcamp-4-3-1-build-the-first-dbt-models-part-6-seeds/).
13. Seed Based dbt Model Creation: dim_zones model
    - create a new model in the Core folder: dim_zones.sql. Note that here instead of creating a view we create a table now. Add the snippet below to the file:
    ```sql
    {{ config(materialized='table') }}

    select 
        locationid, 
        borough, 
        zone, 
        replace(service_zone,'Boro','Green') as service_zone 
    from {{ ref('taxi_zone_lookup') }}
    ```
    - Note that in the above file we replace ‘Green’ with ‘Boro’ in the service_zone field. This is because we want it to be consistent with service_zone ‘Yellow’ naming convention. 
14. Creating a third model - <code>fact_trips.sql</code> model - the second on our Core file
    - This model is referencing both staging models: <code>stg_green_tripdata</code> and <code>stg_yellow_tripdata</code>.
    - I had to remove to field in step 11 which will not be included in this model as a result of it.
    ```sql
    {{
        config(
            materialized='table'
        )
    }}

    with green_tripdata as (
        select *, 
            'Green' as service_type
        from {{ ref('stg_green_tripdata') }}
    ), 
    yellow_tripdata as (
        select *, 
            'Yellow' as service_type
        from {{ ref('stg_yellow_tripdata') }}
    ), 
    trips_unioned as (
        select * from green_tripdata
        union all 
        select * from yellow_tripdata
    ), 
    dim_zones as (
        select * from {{ ref('dim_zones') }}
        where borough != 'Unknown'
    )
    select trips_unioned.tripid, 
        trips_unioned.vendorid, 
        trips_unioned.service_type,
        trips_unioned.ratecodeid, 
        trips_unioned.pickup_locationid, 
        pickup_zone.borough as pickup_borough, 
        pickup_zone.zone as pickup_zone, 
        trips_unioned.dropoff_locationid,
        dropoff_zone.borough as dropoff_borough, 
        dropoff_zone.zone as dropoff_zone,  
        trips_unioned.pickup_datetime, 
        trips_unioned.dropoff_datetime, 
        trips_unioned.store_and_fwd_flag, 
        trips_unioned.passenger_count, 
        trips_unioned.trip_distance, 
        trips_unioned.trip_type, 
        <!-- trips_unioned.fare_amount, 
        trips_unioned.extra, 
        trips_unioned.mta_tax, 
        trips_unioned.tip_amount, 
        trips_unioned.tolls_amount, 
        <!-- trips_unioned.ehail_fee, 
        trips_unioned.improvement_surcharge, 
        trips_unioned.total_amount, 
        trips_unioned.payment_type, 
        trips_unioned.payment_type_description
    from trips_unioned
    inner join dim_zones as pickup_zone
    on trips_unioned.pickup_locationid = pickup_zone.locationid
    inner join dim_zones as dropoff_zone
    on trips_unioned.dropoff_locationid = dropoff_zone.locationid
    ``` 
- the whole point of creating the fact_trips model is to show that we can take both existing models – the staging green trip data and the staging yellow trip data  -->