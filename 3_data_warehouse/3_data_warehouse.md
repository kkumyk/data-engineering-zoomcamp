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
[video source 1](https://www.youtube.com/watch?v=jrHljAoD6nM&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=26) and [video source 2](https://www.youtube.com/watch?v=-CqXf7vhhDs&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=27)

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

### BQ's Best Practices
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






## Learning Material Used
- [Data Warehouse and BigQuery](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse)
- [Alvaro Navas's Notes for this module](https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/3_data_warehouse.md) [and project](https://github.com/ziritrion/dataeng-zoomcamp/tree/main/3_data_warehouse/airflow)