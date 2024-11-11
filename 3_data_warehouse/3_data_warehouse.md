# Data Warehouse and BigQuery

## Table of contents


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
<td>Data view</td>
<td>Lists day-to-day business transactions</td>
<td>Multi-dimensional view of enterprise data</td>
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
    - [On demand pricing (default)](https://cloud.google.com/bigquery/pricing#analysis_pricing_models); the first TB of the month is free.
    - Flat rate pricing based on the number of pre-requested <i>slots</i> (virtual CPUs); makes sense when processing more than 400TB of data per month.

<strong>II. Data Storage</strong>
- [fixed prices](https://cloud.google.com/bigquery/pricing#storage)
- plus additional charges for other operations such as ingestion or extraction

<strong>Please note</strong>:
<i>When running queries on BQ, the top-right corner of the window will display an approximation of the size of the data that will be processed by the query. Once the query has run, the actual amount of processed data will appear in the Query results panel in the lower half of the window. This can be useful to quickly calculate the cost of the query.</i>

### External tables
An <strong>external table</strong> is a table that acts like a standard BQ table. The table metadata (such as the schema) is stored in BQ storage but the data itself is external.

BQ supports a few [external data sources](https://cloud.google.com/bigquery/docs/external-data-sources): you may query these sources directly from BigQuery even though the data itself isn't stored in BQ.


You may create an external table from a CSV or Parquet file stored in a Cloud Storage bucket.

The query below will create an external table based on 2 CSV files. BQ will figure out the table schema and the datatypes based on the contents of the files.

```sql
CREATE OR REPLACE EXTERNAL TABLE `taxi-rides-ny.nytaxi.external_yellow_tripdata`
OPTIONS (
  format = 'CSV',
  uris = ['gs://nyc-tl-data/trip data/yellow_tripdata_2019-*.csv', 'gs://nyc-tl-data/trip data/yellow_tripdata_2020-*.csv']
);
```
Please note, BQ cannot determine processing costs of external tables.

You may import an external table into BQ as a regular internal table by copying the contents of the external table into a new internal table. For example:
```sql
CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_non_partitoned AS
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;
```

### Partitions
- [video source 1](https://www.youtube.com/watch?v=jrHljAoD6nM&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=26)
- [video source 2](https://www.youtube.com/watch?v=-CqXf7vhhDs&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=27)

BQ tables can be partitioned into multiple smaller tables. E.g., if we often filter queries based on date, we could partition a table based on date so that we only query a specific sub-table based on the date we're interested in.

Partition tables are very useful to improve performance and reduce costs, because BQ will not process as much data per query.

tables may be partitioned by:

1. Time-unit column\*: based on a TIMESTAMP, DATE, or DATETIME column in the table.
2. Ingestion time\*: based on the timestamp when BigQuery ingests the data.
3. Integer range:  based on an integer column.

\* <i>the partition may be daily (the default option), hourly, monthly or yearly.</i>

Please note, BQ limits the amount of partitions to 4000 per table. If you need more partitions, consider clustering as well.

Here's an example query for creating a partitioned table:
```sql
CREATE OR REPLACE TABLE taxi-rides-ny.nytaxi.yellow_tripdata_partitoned
PARTITION BY
  DATE(tpep_pickup_datetime) AS
SELECT * FROM taxi-rides-ny.nytaxi.external_yellow_tripdata;
```
BQ will identify partitioned tables with a specific icon. The <i>Details</i> tab of the table will specify the field which was used for partitioning the table and its datatype.


## Learning Material Used
- [Data Warehouse and BigQuery](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse)
- [Alvaro Navas's Notes for this module](https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/3_data_warehouse.md) [and project](https://github.com/ziritrion/dataeng-zoomcamp/tree/main/3_data_warehouse/airflow)