# Data Warehouse and BigQuery

- [Data Warehouse and BigQuery](#data-warehouse-and-bigquery)
  - [OLAP vs OLTP](#olap-vs-oltp)
  - [BigQuery](#bigquery)
    - [Pricing](#pricing)
    - [External Tables](#external-tables)
      - [Main Characteristics of the External Tables](#main-characteristics-of-the-external-tables)
      - [External Table Creation Example (from a DAG)](#external-table-creation-example-from-a-dag)
    - [Partitioned Tables](#partitioned-tables)
      - [Main Characteristics of the Partitioned Tables:](#main-characteristics-of-the-partitioned-tables)
      - [Partitioned Table Creation Example (from a DAG)](#partitioned-table-creation-example-from-a-dag)
    - [Clustering](#clustering)
    - [Partitioning vs Clustering in BQ](#partitioning-vs-clustering-in-bq)
    - [BigQuery's Best Practices](#bigquerys-best-practices)
  - [Integrating BigQuery with Airflow](#integrating-bigquery-with-airflow)
    - [Airflow Setup](#airflow-setup)
    - [Components of the gcs\_2\_bq\_dag.py DAG](#components-of-the-gcs_2_bq_dagpy-dag)
      - [What Does This DAG Do?](#what-does-this-dag-do)
      - [Setup](#setup)
      - [DAG Declaration](#dag-declaration)
      - [Dynamically Iterating Over TAXI\_TYPES](#dynamically-iterating-over-taxi_types)
      - [File Names Parametrization](#file-names-parametrization)
      - [Wrapping Tasks Within a DAG \& Dynamic DAG Creation](#wrapping-tasks-within-a-dag--dynamic-dag-creation)
      - [Tasks](#tasks)
      - [Defined Tasks Dependencies](#defined-tasks-dependencies)
    - [DAG's Execution \& The Output Tables](#dags-execution--the-output-tables)
  - [Learning Material Used](#learning-material-used)

<!-- TOC -->


## OLAP vs OLTP
[video source](https://www.youtube.com/watch?v=jrHljAoD6nM&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=26)

In Data Science, there are 2 main types of data processing systems:

1. <strong>OLTP</strong> (Online Transaction Processing): "classic databases"
2. <strong>OLAP</strong> (Online Analytical Processing): catered for advanced data analytics purposes, e.g:
    - a Data Warehouse (DW) which commonly use ETL model:
        - a DW receives data from different <strong>data sources</strong>
        - the data is then processed in a <strong>staging area</strong> before being ingested to the actual warehouse (a database)
        - DWs may then feed data to separate <strong>Data Marts</strong> - subsets of a DWs / smaller database systems which end users may use for different purposes.

<table>
<thead>
<tr>
<th></th>
<th>OLTP</th>
<th>OLAP</th>
</tr>
</thead>
<tbody>
<tr>
<td>Purpose</td>
<td>Control and run essential business operations in real time</td>
<td>Plan, solve problems, support decisions, discover hidden insights</td>
</tr>
<tr>
<td>Data updates</td>
<td>Short, fast updates initiated by user</td>
<td>Data periodically refreshed with scheduled, long-running batch jobs</td>
</tr>
<tr>
<td>Database design</td>
<td>Normalized databases for efficiency</td>
<td>Denormalized databases for analysis</td>
</tr>
<tr>
<td>Space requirements</td>
<td>Generally small if historical data is archived</td>
<td>Generally large due to aggregating large datasets</td>
</tr>
<tr>
<td>Backup and recovery</td>
<td>Regular backups required to ensure business continuity and meet legal and governance requirements</td>
<td>Lost data can be reloaded from OLTP database as needed in lieu of regular backups</td>
</tr>
<tr>
<td>Productivity</td>
<td>Increases productivity of end users</td>
<td>Increases productivity of business managers, data analysts and executives</td>
</tr>
<tr>
<td>Data view</td>to manually add new tasks for each new taxi typee data</td>
</tr>
<tr>
<td>User examples</td>
<td>Customer-facing personnel, clerks, online shoppers</td>
<td>Knowledge workers such as data analysts, business analysts and executives</td>
</tr>
</tbody>
</table>

## BigQuery
- a DW offered by Google Cloud Platform
- serverless (no servers to manage or database software to install);
- scalable and has high availability
- has built-in features like Machine Learning, Geospatial Analysis and Business Intelligence
- maximizes flexibility by separating data analysis and storage in different compute engines, allowing the customers to budget accordingly and reduce costs
- BQ alternatives from other cloud providers: AWS Redshift or Azure Synapse Analytics

### Pricing
Pricing divided in 2 main components:
    
<strong>I. Data Processing</strong>

- has a 2-tier pricing model:
    - [On demand pricing (default)](https://cloud.google. based on dateth.

<strong>II. Data Storage</strong>
- [fixed prices](https://cloud.google.com/bigquery/pricing#storage)
- plus additional charges for other operations such as ingestion or extraction

<strong>Please note</strong>:
<i>When running queries on BQ, the top-right corner of the window will display an approximation of the size of the data that will be processed by the query. Once the query has run, the actual amount of processed data will appear in the Query results panel in the lower half of the window. This can be useful to quickly calculate the cost of the query.</i>

### [External Tables](https://cloud.google.com/bigquery/docs/tables-intro#external_tables)

<strong>External tables</strong> in BigQuery are tables stored outside out of BigQuery storage and refer to data that's stored outside of BigQuery, typically in Google Cloud Storage (GCS). 

An <strong>external table</strong> is a table that acts like a [standard BQ table](https://cloud.google.com/bigquery/docs/tables-intro#standard_tables). The table metadata (such as the schema) is stored in BQ storage but the data itself is external. The data is not physically stored in BigQuery. Instead, BigQuery queries the data directly from its external location. (BQ supports a few [external data sources](https://cloud.google.com/bigquery/docs/external-data-sources): you may query these sources directly from BigQuery even though the data itself isn't stored in BQ.)

#### Main Characteristics of the External Tables
- points to data in an external source, such as GCS
- the data is not physically copied into BigQuery; it remains stored in GCS
- the external table is linked to data stored in a particular format, e.g.: Parquet
- BQ can auto-detect the schema of the external data; this is helpful when you don’t know the schema in advance; you can define the schema explicitly when creating the external table
- queries on the external table can be run in the same way as on any other BQ table, but BQ reads the data from GCS when running the queries; this can introduce some latency because data isn't stored within BQ itself
- useful for when you need to query large datasets stored in GCS without the need to load the data into BQ
- BQ cannot determine processing costs of external tables
  
You may create an external table from a CSV or Parquet file stored in a Cloud Storage bucket.

The query below will create an external table based on 2 CSV files. BQ will figure out the table schema and the datatypes based on the contents of the files.

```sql
CREATE OR REPLACE EXTERNAL TABLE `taxi-rides-ny.nytaxi.external_yellow_tripdata`
OPTIONS (
  format = 'CSV',
  uris = ['gs://nyc-tl-data/trip data/yellow_tripdata_2019-*.csv', 'gs://nyc-tl-data/trip data/yellow_tripdata_2020-*.csv']
);
```

You may import an external table into BQ as a regular internal table by copying the contents of the external table into a new internal table. For example:
```sql
CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_non_partitoned AS
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;
```

#### External Table Creation Example (from a DAG)
An external table is created in BQ which points to the Parquet files stored in GCS (gs://{BUCKET}/{taxi_type}/*):

```python
gcs_2_bq_ext_task = BigQueryCreateExternalTableOperator(
  task_id=f"bq_{taxi_type}_{DATASET}_external_table_task",
  table_resource={
      "tableReference": {
          "projectId": PROJECT_ID,
          "datasetId": BIGQUERY_DATASET,
          "tableId": f"{taxi_type}_{DATASET}_external_table",
      },
      "externalDataConfiguration": {
          "autodetect": "True",
          "sourceFormat": "PARQUET",
          "sourceUris": [f"gs://{BUCKET}/{taxi_type}/*"],
      },
  },
)
```

### [Partitioned Tables](https://cloud.google.com/bigquery/docs/partitioned-tables)
[video source 1](https://www.youtube.com/watch?v=jrHljAoD6nM&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=26) and [video source 2](https://www.youtube.com/watch?v=-CqXf7vhhDs&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=27)

BQ tables can be partitioned into multiple smaller tables. E.g., if we often filter queries based on date, we could partition a table based on date so that we only query a specific sub-table based on the date we're interested in.

<strong>Partitioned tables</strong> are very useful to improve performance and reduce costs, because BQ will not process as much data per query.

<strong>Partitioned table</strong>  in BQ is a table that stores data physically within BQ, and the data is partitioned into smaller, manageable segments based on a specified column, usually a timestamp or date column. Partitioning improves performance by reducing the amount of data scanned when running queries.

#### Main Characteristics of the Partitioned Tables:
- the data is physically stored within BQ
- data is loaded into BQ (as opposed to an external table where the data remains in GCS)
- data is divided into partitions, which are subsets of the data based on the values in a column, often used for time-series or date-based data
- partitioned tables help optimize query performance because BQ only scans the relevant partitions of the table based on the query; for example, if a query filters by a specific date range, BQ only scans the partitions corresponding to that range
- the schema of the partitioned table is explicitly defined, and data must adhere to the schema when it is loaded into BQ
- ideal for large datasets where performance and cost optimization are important because partitioning helps limit the amount of data read by each query

Tables may be partitioned by:

1. Time-unit column\*: based on a TIMESTAMP, DATE, or DATETIME column in the table.
2. Ingestion time\*: based on the timestamp when BigQuery ingests the data.
3. Integer range: based on an integer column.

\* <i>the partition may be daily (the default option), hourly, monthly or yearly.</i>

Please note, BQ limits the amount of partitions to 4000 per table. If you need more partitions, consider clustering as well.

Here's an example query for creating a [partitioned table](https://cloud.google.com/bigquery/docs/partitioned-tables?_gl=1*z2wu5*_ga*MTM5MDIyMzM4Ny4xNzE5ODQwNjYw*_ga_WH2QY8WWF5*MTczMTY3Nzg4Ni4zNS4xLjE3MzE2Nzg0ODUuMzguMC4w):
```sql
CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_partitoned
PARTITION BY
  DATE(tpep_pickup_datetime) AS
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;
```
BQ will identify partitioned tables with a specific icon. The <i>Details</i> tab of the table will specify the field which was used for partitioning the table and its datatype.

#### Partitioned Table Creation Example (from a DAG)

In the example below partitioned table is created by querying the external table. The new table is partitioned based on the specified column (ds_col), which is typically a date or timestamp column, here: tpep_pickup_datetime:

```python
CREATE_BQ_TBL_QUERY = (
    f"CREATE OR REPLACE TABLE {BIGQUERY_DATASET}.{taxi_type}_{DATASET} \
    PARTITION BY DATE({ds_col}) \
    AS \
    SELECT * FROM {BIGQUERY_DATASET}.{taxi_type}_{DATASET}_external_table;"
)

bq_ext_2_part_task = BigQueryInsertJobOperator(
    task_id=f"bq_create_{taxi_type}_{DATASET}_partitioned_table_task",
    configuration={
        "query": {
            "query": CREATE_BQ_TBL_QUERY,
            "useLegacySql": False,
        }
    }
)
```

### Clustering

[video source 1](https://www.youtube.com/watch?v=jrHljAoD6nM&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=27) and 
[video source 2](https://www.youtube.com/watch?v=-CqXf7vhhDs&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=27)

- consists of rearranging a table based on the values of its columns so that the table is ordered according to any criteria
- can be done based on one or multiple columns up to 4
- the order of the columns in which clustering is specified is important in order to determine the column priority
- may improve performance and lower costs on big datasets for certain types of queries, such as queries that use filter clauses and queries that aggregate data

<strong><i>Please note</i></strong>:
- tables with less than 1GB don't show significant improvement with partitioning and clustering;
- doing so in a small table could even lead to increased cost due to the additional metadata reads and maintenance needed for these features.

Clustering columns must be top-level, non-repeated columns. The following data types are supported:
- DATE
- BOOL
- GEOGRAPHY
- INT64
- NUMERIC
- BIGNUMERIC
- STRING
- TIMESTAMP
- DATETIME

A partitioned table can also be clustered.

### Partitioning vs Clustering in BQ
[video source](https://www.youtube.com/watch?v=-CqXf7vhhDs&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=27)
<table>
<thead>
<tr>
<th>Clustering</th>
<th>Partitioning</th>
</tr>
</thead>
<tbody>
<tr>
<td>Cost benefit unknown. BQ cannot estimate the reduction in cost before running a query.</td>
<td>Cost known upfront. BQ can estimate the amount of data to be processed before running a query.</td>
</tr>
<tr>
<td>High granularity. Multiple criteria can be used to sort the table.</td>
<td>Low granularity. Only a single column can be used to partition the table.</td>
</tr>
<tr>
<td>Clusters are "fixed in place".</td>
<td>Partitions can be added, deleted, modified or even moved between storage options.</td>
</tr>
<tr>
<td>Benefits from queries that commonly use filters or aggregation against multiple particular columns.</td>
<td>Benefits when you filter or aggregate on a single column.</td>
</tr>
<tr>
<td>Unlimited amount of clusters; useful when the cardinality of the number of values in a column or group of columns is large.</td>
<td>Limited to 4000 partitions; cannot be used in columns with larger cardinality.</td>
</tr>
</tbody>
</table>

<i><strong>Choose clustering over partitioning when</i></strong>:
- partitioning results in a small amount of data per partition
- partitioning would result in over 4000 partitions
- if your mutation operations modify the majority of partitions in the table frequently (for example, writing to the table every few minutes and writing to most of the partitions each time rather than just a handful)

BQ has <i><strong>automatic reclustering</i></strong>: when new data is written to a table, it can be written to blocks that contain key ranges that overlap with the key ranges in previously written blocks, which weaken the sort property of the table. BQ will perform automatic reclustering in the background to restore the sort properties of the table.

For partitioned tables, clustering is maintained for data within the scope of each partition.

### BigQuery's Best Practices
[video source](https://www.youtube.com/watch?v=k81mLJVX08w&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=28)

Here is a [list of best practices for BQ](https://cloud.google.com/bigquery/docs/best-practices-performance-overview):

<strong> I. Cost reduction</strong>

- Avoid <code>SELECT *</code>. Reducing the amount of columns to display will drastically reduce the amount of processed data and lower costs.
- Price your queries before running them.
- Use clustered and/or partitioned tables if possible.
- Use [streaming inserts](https://cloud.google.com/bigquery/docs/streaming-data-into-bigquery) with caution. They can easily increase cost.
- [Materialize query results](https://cloud.google.com/bigquery/docs/materialized-views-intro) in different stages.

<strong> II. Query performance</strong>

- Filter on partitioned columns.
- [Denormalize data](https://cloud.google.com/blog/topics/developers-practitioners/bigquery-explained-working-joins-nested-repeated-data).
- Use [nested or repeated columns](https://cloud.google.com/blog/topics/developers-practitioners/bigquery-explained-working-joins-nested-repeated-data).
- Use external data sources appropriately. Constantly reading data from a bucket may incur in additional costs and has worse performance.
- Reduce data before using a JOIN.
- Do not threat <code>WITH</code> clauses as [prepared statements](https://www.wikiwand.com/en/articles/Prepared_statement).
- Avoid [oversharding tables](https://cloud.google.com/bigquery/docs/partitioned-tables#dt_partition_shard).
- Avoid JavaScript user-defined functions.
- Use [approximate aggregation functions](https://cloud.google.com/bigquery/docs/reference/standard-sql/approximate_aggregate_functions) rather than complete ones such as [HyperLogLog++](https://cloud.google.com/bigquery/docs/reference/standard-sql/hll_functions).
- Order statements should be the last part of the query.
- [Optimize join patterns](https://cloud.google.com/bigquery/docs/best-practices-performance-compute#optimize_your_join_patterns).
- Place the table with the <i>largest</i> number of rows first, followed by the table with the <i>fewest</i> rows, and then place the remaining tables by decreasing size.
This is due to how BigQuery works internally: the first table will be distributed evenly and the second table will be broadcasted to all the nodes. Check the Internals section for more details. This is due to how BigQuery works internally: the first table will be distributed evenly and the second table will be broadcasted to all the nodes. Check the Internals section for more details.

## Integrating BigQuery with Airflow
We will now use Airflow to automate the creation of BQ tables, both normal and partitioned.

### Airflow Setup

Docker, requirements.txt and env files are taken as they are from the [airflow_gcp](https://github.com/kkumyk/data-engineering-zoomcamp/tree/main/2_workflow_orchestration/airflow_gcp) directory of the previous module. The DAG file is replaced with the one from the next section below.

### Components of the gcs_2_bq_dag.py DAG

#### What Does This DAG Do?
This DAG is designed to automate the process of <i><strong>moving data from Google Cloud Storage (GCS) to Google BigQuery (BQ)</strong></i>.

#### Setup
- The DAG will use the official Google-provided operators, see Tasks section below and the imports section of the DAG itself.
- The tasks are dynamically created for each taxi_type (yellow, green, fhv) in the <code>TAXI_TYPES</code> dictionary.

#### DAG Declaration

The DAG object below wraps all the tasks and defines the overall workflow:
```python
with DAG(
    dag_id="gcs_2_bq_dag",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:
```
Params include:
- dag_id: unique identifier for the DAG (gcs_2_bq_dag)
- schedule_interval: the frequency at which the DAG runs, here, @daily
- default_args: a dictionary that contains default parameters for the tasks in the DAG (retries, start date, etc)
- catchup=False: makes sure the DAG doesn't backfill past runs if it was not run on time
- max_active_runs=1: limits the number of active DAG runs that can be executed concurrently
- tags: used to categorize the DAG, making it easier to search and organize in the Airflow UI.

#### Dynamically Iterating Over TAXI_TYPES
The loop iterates over the TAXI_TYPES dictionary, which contains the key-value pairs for each taxi type ('yellow', 'green', 'fhv') and the associated column (tpep_pickup_datetime, Pickup_datetime, lpep_pickup_datetime) used for partitioning in BigQuery:
  ```python 
  TAXI_TYPES =
      {'yellow': 'tpep_pickup_datetime',
      'fhv': 'Pickup_datetime',
      'green': 'lpep_pickup_datetime'}

  for taxi_type, ds_col in TAXI_TYPES.items():
  ```

#### File Names Parametrization

We are not going to use a specific file type in this DAG and will parametrize the filenames so that we can loop through all of them. This way the DAG becomes more flexible in terms of the types of files it can handle by copying files of any type (e.g.: csv, .json, .parquet, etc.) without modifying the DAG should the file type changes:
```python
#INPUT_FILETYPE = "parquet"

#source_object=f'{INPUT_PART}/{taxi_type}_*.{INPUT_FILETYPE}',
source_object=f'{INPUT_PART}/{taxi_type}_*',

#destination_object=f'{taxi_type}/{taxi_type}_{DATASET}*.{INPUT_FILETYPE}',
destination_object=f'{taxi_type}/{taxi_type}_',
```
#### Wrapping Tasks Within a DAG & Dynamic DAG Creation
- We wrap all tasks within the DAG in a for loop to create tasks and loop through the taxi types.
- By using the for loop  inside the DAG context (with DAG(...) as dag:):
  - the tasks are <strong>automatically added to the DAG</strong>, meaning
  - that all tasks are <strong>logically grouped together under a single DAG</strong>, but
  - they are <strong>dynamically created</strong> based on the number of taxi types.
- By wrapping the task creation within a loop means that the DAG can handle an arbitrary number of taxi types and corresponding tasks. By adding more taxi types to TAXI_TYPES, the DAG will automatically generate new tasks for them without modifying the DAG structure. No need to manually add new tasks for each new taxi type.


#### Tasks
The DAG contains 3 tasks:

1. the <code>gcs_2_gcs</code> task moves files from GCS to GCS:
   - uses <code>[GCSToGCSOperator](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/_api/airflow/providers/google/cloud/transfers/gcs_to_gcs/index.html)</code> that moves files from one location in a GCS bucket to another;
     <!-- - the <code>GCSToGCSOperator</code> is used to move files from one location in a GCS bucket to another;   -->
   <!-- The files are organized by taxi_type, and the source_object pattern ({taxi_type}_*) suggests it is dealing with different types of taxi data (e.g., Yellow, FHV, Green) that may have varying file formats or naming conventions. -->

2. the <code>gcs_2_bq_ext</code> creates an external table in BigQuery:
    - uses <code>[BigQueryCreateExGoogle Cloud Storage (GCS) to Google BigQuery (BQ)lTableOperator)</code> that creates an external table
    - the external table uses Parquet as its source format and autodetects the schema based on the files.
    - the external table is used to query the data without loading it into BigQuery.
    <!-- - the <code>BigQueryCreateExternalTableOperator</code> creates an external table in BigQuery, pointing to the files in GCS that were moved in the first step. -->
3. the <code>bq_ext_2_part</code> task partitions data in BigQuery:
     - uses <code>[BigQueryInsertJobOperator](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/_api/airflow/providers/google/cloud/operators/bigquery/index.html#airflow.providers.google.cloud.operators.bigquery.BigQueryInsertJobOperator)</code> that creates a partitioned table
    <!-- - <code>BigQueryInsertJobOperator</code> runs a SQL query that creates a partitioned table in BigQuery, based on a column (ds_col) that depends on the taxi_type. -->

      <!-- For example:
          For Yellow Taxi data, it uses the column tpep_pickup_datetime.
          For FHV data, it uses Pickup_datetime.
          For Green Taxi data, it uses lpep_pickup_datetime.
      The partitioning is done on the date (PARTITION BY DATE(...)), so this query creates a partitioned table where the data is divided by the pickup date (as indicated by the relevant column for each taxi type). -->

#### Defined Tasks Dependencies

  ```py
  gcs_2_gcs_task >> gcs_2_bq_ext_task >> bq_ext_2_part_task
  ```

### DAG's Execution & The Output Tables

1. Build the image:
  ```shell
  docker compose build 
  ```
  You only need to do this the first time you run Airflow or if you modified the Dockerfile or the requirements.txt file.

2. Initialize configs:
```shell
docker compose up airflow-init
```
3. Run Airflow in a detached mode
```shell
docker compose up -d
```
4. Open Airflow GUI by browsing to localhost:8080. Username and password are both airflow.

  ```shell
  # IMPORTANT: this is NOT a production-ready setup! The username and password for Airflow have not been modified in any way; you can find them by searching for _AIRFLOW_WWW_USER_USERNAME and _AIRFLOW_WWW_USER_PASSWORD inside the docker-compose.yaml file.
  ```
5. Run your DAG on the Web Console.

<img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/3_data_warehouse/_doc/gcs_2_bq_dag_run_results.png" alt="DAG run result in Airflow" width="600"/>

6. The output result of running the DAG are two tables:
  - a normal external table: <i>yellow_tripdata_external_table</i>
  - a partitioned table: <i>yellow_tripdata</i>

<img src="https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/3_data_warehouse/_doc/gcs_to_bg_results.png" alt="DAG run result in Airflow" width="600"/>

7. On finishing your run or to shut down the container/s:
  ```shell
  docker compose down -v  
  ```

## Learning Material Used
- [Data Warehouse and BigQuery](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse)
- [Alvaro Navas's Notes for this module](https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/3_data_warehouse.md) [and project](https://github.com/ziritrion/dataeng-zoomcamp/tree/main/3_data_warehouse/airflow)