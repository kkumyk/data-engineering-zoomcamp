
# Docker and Postgres

## 1. Creating a Custom Pipeline with Docker

[video source: 1.2.1](https://www.youtube.com/watch?v=EYNwNlOrpr0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=4)

The simple pipeline pipeline.py is a Python script that receives an argument and prints it:
```bashhttps://www.youtube.com/watch?v=2JM-ziJt0WI&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=5
import sys
import pandas # is used here for the containerization example later on

# print arguments
print(sys.argv)

# argument 1 contains the actual first argument
nr_o_pizzas = sys.argv[1]

# print a sentence with the argument
print(f'Job finished successfully! Celebrate it with {nr_o_pizzas} pizzas!') 
```
We can run this script with <i>python  pipeline.py <some_number></i> and it will print two lines:

```bash
['pipeline.py', '10']
Job finished successfully! Celebrate it with 10 pizzas!
```
Let's containerize the pipeline by creating a Docker image. Create a Dockerfile file in the same directory as your <i>pipeline.py</i>:

```bash
# use an official Python runtime as a parent image
FROM python:3.11-slim

# install Poetry
RUN pip install poetry

# copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock ./

# install dependencies via Poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# set up the working directory inside the container
WORKDIR /app

# copy the script to the container.
# 1st name is source file, 2nd is destination
COPY pipeline.py pipeline.py

# define what to do first when the container runs
# in this example, we will just run the script
ENTRYPOINT ["python", "pipeline.py"]
```
Let's build the image where <i>first_image</i> will be the name of the image and its tag will be pandas:
```bash
docker build -t first_image:pandas .
```
To run the container, pass an argument to it so that our pipeline will receive it:

```bash
docker run -it first_image:pandas 10
```
The output result will be the same as when we run the pipeline by itself without using Docker:
```bash
['pipeline.py', '10']
Job finished successfully. Celebrate it with 10 pizzas.
```

## 2. Running Postgres in a Docker Container

[video source: 1.2.2](https://www.youtube.com/watch?v=2JM-ziJt0WI&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=5)

<i>mounting</i> - mapping of a folder on the host machine to a folder in a Docker container

### Creating a Postgres Database

To run Postgres in a Docker container we need to provide a few environment variables <i>volume</i> for data storage to persist the data. For this to work:

1. Create a ny_taxi_postgres_data folder where you want to store the data.
2. Navigate to the folder where the above folder lives.
3. On the command line run the command below:
    ```bash
    docker run -it \
        -e POSTGRES_USER="your_user_name" \
        -e POSTGRES_PASSWORD="your_db_password" \
        -e POSTGRES_DB="ny_taxi" \
        -v ny_taxi_postgres_data:/var/lib/postgresql/data \
        -p 5432:5432 \
        postgres:15
    ```
    - POSTGRES_USER is the username for logging into the database.
    - POSTGRES_PASSWORD is the password for the database. 
    - POSTGRES_DB is the name that we will give the database.
    - v points to the volume directory. The colon separates:
        - the first part - path to the folder on the host computer <i>from</i>
        - the second part - path to the folder inside the container.
    - The -p is for port mapping. We map the default Postgres port to the same port in the host.
    - The last argument is the image name and tag. We run the official postgres image on its version 15.

#### Issue Encountered:
```
docker: Error response from daemon: Ports are not available: exposing port TCP 0.0.0.0:5432 -> 0.0.0.0:0: listen tcp 0.0.0.0:5432: bind: address already in use.
```
This above error indicates that the port 5432, which we are trying to expose in Docker, is already in use by another process on our host machine. This usually happens when another service (such as a local PostgreSQL server) is already running and using that port.

To resolve the issue above follow the the steps below:

1. Find the process using the port on Linux:

```bash
sudo lsof -i :5432
```
2. Stop the process using its PID:
```bash
sudo kill 1234
```
3. Re-run the command containing the env vars and volume location.

### Testing the Connection

Once the container is running, we can log into our database using the following command:
```bash
psql -h localhost -U your_user_name -d ny_taxi
```
- <i>ny_taxi</i> is the name of the database we created with the command from the previous section. 
- The password will be requested after running the command above (the one set with the command from the previous section).

## 3. Ingesting NY Trips Data to Postgres DB with Python

1. Update Dependencies by adding sqlalchemy, pyarrow and psycopg2 to poetry lock file.
2. Download [parquet file](https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet) ([source](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)) and save it into the same folder as the ny_taxi_postgres_data subfolder.
3. Run Docker container and connect to your Postgres db as per steps from the previous section.
4. Once connected to db, CREATE TABLE with the schema below:
```bash
CREATE TABLE yellow_taxi_data (
	VendorID INTEGER, 
	tpep_pickup_datetime TIMESTAMP WITHOUT TIME ZONE, 
	tpep_dropoff_datetime TIMESTAMP WITHOUT TIME ZONE, 
	passenger_count FLOAT(53), 
	trip_distance FLOAT(53), 
	RatecodeID FLOAT(53), 
	store_and_fwd_flag TEXT, 
	PULocationID INTEGER, 
	DOLocationID INTEGER, 
	payment_type BIGINT, 
	fare_amount FLOAT(53), 
	extra FLOAT(53), 
	mta_tax FLOAT(53), 
	tip_amount FLOAT(53), 
	tolls_amount FLOAT(53), 
	improvement_surcharge FLOAT(53),
	total_amount FLOAT(53), 
	congestion_surcharge FLOAT(53), 
	Airport_fee FLOAT(53)
);
```
5. Run <i>ingest_data.py</i> file to load the data from the parquet file into the <i>yellow_taxi_data</i> table:
```bash
poetry run python ingest_data.py --user=YOUR-USER --password=YOUR_PASSWORD --host=localhost --port=5432 --db=ny_taxi --tb=yellow_taxi_data --url=YOU-URL
```
6. Verify the ingestion with:
```sql
select * from yellow_taxi_data limit 5;
```

## 4. Connecting pgAdmin and Postgres with Docker

[pgAdmin](https://www.pgadmin.org/) - a convenient web-based tool to access and manage out databases.

We will run pgAdmin as a container along with the Postgres container, but both containers will have to be in the same <i>virtual network</i> so that they can find each other. For this to happen:

1. Create a virtual Docker network called pg-network:

```bash
docker network ls # list existing networks

docker network create pg-network # create network named pg-network

docker network remove rm pg-network # remove network named pg-network if not in use
```
2. Re-run your Postgres container

    This time we will also add the <b>network name</b> and the <b>container network name - pg-db</b>. This way the pgAdmin container will find the Postgres container.

    ```bash
    docker run -it \
        -e POSTGRES_USER="your_user_name" \
        -e POSTGRES_PASSWORD="your_db_password" \
        -e POSTGRES_DB="ny_taxi" \
        -v ny_taxi_postgres_data:/var/lib/postgresql/data \
        -p 5432:5432 \
        --network=pg-network \
        --name pg-db \
        postgres:15
    ```
3. Now run the pgAdmin container on another terminal. Replace the email and password values before running this container. To tun pgAdmin in docker use the command below:

```bash
docker run -it \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    -p 8080:80 \
    --network=pg-network \
    --name pgadmin \
    dpage/pgadmin4
```
- You should be able to load pgAdmin in your browser under localhost:8080. Log in with the specified log-in email and password.
- pgAdmin is a web app and its default port is 80; we map it to 8080 in our localhost to avoid any possible conflicts.
- Just as with the Postgres container we specify a network and a name. However, the name in this example is not necessary as there won't be any containers trying to access this particular container.
- The image name is dpage/pgadmin4
<br>
4. Configure server:

    - Servers > Register Server
    - Under <i>General</i> give the Server a name, e.g.: Docker localhost 
    - Under <i>Connection</i> add the same host name, user and password you used when running your Postgres container.
    - Host name/address will be the name specified in the command for running the Posgres container. Same for the user name.
    - After saving the configurations, you should be connected to the database.
    - Create yellow_taxi_data table and run ingest_data.py script on parquet and csv files to add taxi and zones data to the Postgres database. See instructions in the section 3.

## 5. Dockerizing ingest_data.py

## 6. Running Postgres and pgAdmin with Docker-compose

In section 4 we made two containers talk to each other via the same network. This was done by running two command line commands. In this section we replace that process with a yaml file that will contain the instructions for the same process to happen from a single source.


<br>
<hr>

# SQL Refresher
[video source: 1.2.6](https://www.youtube.com/watch?v=QEcps_iskgg&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=10)

The examples below are working two tables:

- yellow_taxi_data
- zones

    Add table <i>zones</i> to Postgres db by downloading the Taxi Zone Lookup Table (CSV) [here](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) and ingesting the data using <i>ingest_data.py</i>.

## 1. View the first 100 rows of the yellow_taxi_data table

Select all rows from the table. If there are more than 100 rows, select the first 100:
```sql
select * from yellow_taxi_data limit 100; 
```
## 2. View tables' contents

After running the query below we can view the contents yellow_taxi_data and the zones tables in one view. This is done by assigning alias to tables in the FROM statement and navigating to specific columns via the specified alias after the WHERE statement: 

```sql
select
    *
from
    yellow_taxi_data t,
    zones zpu,
    zones zdo
where
    t."PULocationID" = zpu."LocationID" and
    t."DOLocationID" = zdo."LocationID"
limit 100;
```
The result view looks clattered as the contents of the zones tables are returned twice as location ID matched twice - the pull-up and drop-off locations in the yellow_taxi_data table.  

## 3. Use Inner Join to select overlapping rows between 2 tables
We only display specific columns using implicit joins and combining (concatenating) pieces of information into a single column - "pickup_loc". It contains the borough and zone information. Same for the "dropoff_loc".

For more on SQL Joins see [SQL Join types explained visually](https://www.atlassian.com/data/sql/sql-join-types-explained-visually) and [Join (SQL)](https://www.wikiwand.com/en/articles/Join_(SQL)).
 

```sql
SELECT
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    total_amount,
    CONCAT(zpu."Borough", '/', zpu."Zone") AS "pickup_loc",
    CONCAT(zdo."Borough", '/', zdo."Zone") AS "dropoff_loc"
FROM
    yellow_taxi_data t,
    zones zpu,
    zones zdo
WHERE
    t."PULocationID" = zpu."LocationID" AND
    t."DOLocationID" = zdo."LocationID"
LIMIT 100;

-- tpep_pickup_datetime  | tpep_dropoff_datetime | total_amount |               pickup_loc                |               dropoff_loc               
-- ----------------------+-----------------------+--------------+-----------------------------------------+----------------------------------
--  2024-01-01 00:57:55  | 2024-01-01 01:17:43   |         22.7 | Manhattan/Penn Station/Madison Sq West  | Manhattan/East Village
--  2024-01-01 00:03:00  | 2024-01-01 00:09:36   |        18.75 | Manhattan/Lenox Hill East               | Manhattan/Upper East Side North
--  2024-01-01 00:17:06  | 2024-01-01 00:35:01   |         31.3 | Manhattan/Upper East Side North         | Manhattan/East Village
--  2024-01-01 00:46:51  | 2024-01-01 00:52:57   |         16.1 | Manhattan/SoHo                          | Manhattan/Lower East Side
--  2024-01-01 00:54:08  | 2024-01-01 01:26:31   |         41.5 | Manhattan/Lower East Side               | Manhattan/Lenox Hill West

```
Same but using explicit Inner Join:

```sql
SELECT
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    total_amount,
    CONCAT(zpu."Borough", '/', zpu."Zone") AS "pickup_loc",
    CONCAT(zdo."Borough", '/', zdo."Zone") AS "dropoff_loc"
FROM
    yellow_taxi_data t JOIN zones zpu
        ON t."PULocationID" = zpu."LocationID"
    JOIN zones zdo
        ON t."DOLocationID" = zdo."LocationID"
LIMIT 100;

-- tpep_pickup_datetime | tpep_dropoff_datetime | total_amount |               pickup_loc                |               dropoff_loc               
-- ----------------------+-----------------------+--------------+-----------------------------------------+-----------------------------------------
--  2024-01-01 00:57:55  | 2024-01-01 01:17:43   |         22.7 | Manhattan/Penn Station/Madison Sq West  | Manhattan/East Village
--  2024-01-01 00:03:00  | 2024-01-01 00:09:36   |        18.75 | Manhattan/Lenox Hill East               | Manhattan/Upper East Side North
--  2024-01-01 00:17:06  | 2024-01-01 00:35:01   |         31.3 | Manhattan/Upper East Side North         | Manhattan/East Village
--  2024-01-01 00:46:51  | 2024-01-01 00:52:57   |         16.1 | Manhattan/SoHo                          | Manhattan/Lower East Side
--  2024-01-01 00:54:08  | 2024-01-01 01:26:31   |         41.5 | Manhattan/Lower East Side               | Manhattan/Lenox Hill West

```
## 4. Check for Null values

Return rows where the pick up location is not specified:
```sql
SELECT
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    total_amount,
    "PULocationID",
    "DOLocationID"
FROM
    yellow_taxi_data t
WHERE
    "PULocationID" is NULL
LIMIT 100;

-- Should return an empty table if the original dataset in not modified:
--  tpep_pickup_datetime | tpep_dropoff_datetime | total_amount | PULocationID | DOLocationID 
-- ----------------------+-----------------------+--------------+--------------+--------------
-- (0 rows)
```

Check if there are any rows where drop off location ID does not appear in the zones table:

```sql
select
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    total_amount,
    "PULocationID",
    "DOLocationID"
from yellow_taxi_data t
where "DOLocationID" not in (select "LocationID" from zones)
limit(100);

-- Similar to the join query from before but we use a left join instead.
-- n an empty table if the original dataset in not modified:

--  tpep_pickup_datetime | tpep_dropoff_datetime | total_amount | PULocationID | DOLocationID 
-- ----------------------+-----------------------+--------------+--------------+--------------
-- (0 rows)

-- -- modify the zones table by deleting a specific location ID:
-- delete from zones where "LocationID" = 142;

-- -- the re-run of the previous query returns only rows where drop off location ID is 142:
--  tpep_pickup_datetime | tpep_dropoff_datetime | total_amount | PULocationID | DOLocationID 
-- ----------------------+-----------------------+--------------+--------------+--------------
--  2024-01-01 00:45:51  | 2024-01-01 00:49:43   |         13.8 |          238 |          142
--  2024-01-01 00:55:58  | 2024-01-01 01:03:54   |           17 |          238 |          142
--  2024-01-01 00:38:04  | 2024-01-01 00:42:53   |         13.5 |          143 |          142
--  2024-01-01 00:33:59  | 2024-01-01 00:39:53   |        15.86 |           48 |          142
--  2024-01-01 00:05:09  | 2024-01-01 00:40:40   |         48.5 |          148 |          142...

```

## 5. Left Join
Left joins show all rows from the left part of the statement - the table add on the left side of the statement - and the rows from the right table that overlap with the left one.

Left joins are used when dealing with missing values. As opposed to Inner Join, the rows that could not be matched in both tables, will be omitted in the returned table.

Return all rows from yellow_taxi_data table even if a zone does not exist in the zones table:
```sql
select 	tpep_pickup_datetime,
		tpep_dropoff_datetime,
		total_amount,
		concat(zpu."Borough", '/', zpu."Zone") as "Pickup Location",
		concat(zdo."Borough", '/', zdo."Zone") as "Drop off Location"
from yellow_taxi_data y
left join zones zpu on "PULocationID" = zpu."LocationID"
left join zones zdo on "DOLocationID" = zdo."LocationID"
limit 100;

--  tpep_pickup_datetime | tpep_dropoff_datetime | total_amount |             Pickup Location             |             Drop off Location             
-- ----------------------+-----------------------+--------------+-----------------------------------------+------------------------------------------
--  2024-01-01 00:34:38  | 2024-01-01 00:52:39   |         25.4 | Manhattan/SoHo                          | Manhattan/Murray Hill
--  2024-01-01 00:42:43  | 2024-01-01 01:06:35   |        98.88 | Queens/JFK Airport                      | Manhattan/Kips Bay
--  2024-01-01 00:21:02  | 2024-01-01 00:23:33   |        11.28 | Manhattan/Gramercy                      | Manhattan/Greenwich Village North
--  2024-01-01 00:30:35  | 2024-01-01 00:55:19   |        35.38 | Manhattan/SoHo                          | Manhattan/East Chelsea
--  2024-01-01 00:56:04  | 2024-01-01 01:50:23   |         68.1 | Manhattan/East Chelsea                  | Manhattan/Yorkville West
--  2024-01-01 00:14:59  | 2024-01-01 00:19:52   |         14.2 | Manhattan/Yorkville West                | Manhattan/Lenox Hill West

```

## 6. Remove the time using CAST

Show a column with the date of the transaction only by removing the time and returning YYYY-MM-DD:

```sql
select 
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    cast(tpep_pickup_datetime as date) as "YYYY-MM-DD",
    total_amount as "Total Amount"
from yellow_taxi_data
limit 100;

--  tpep_pickup_datetime | tpep_dropoff_datetime | YYYY-MM-DD | Total Amount 
-- ----------------------+-----------------------+------------+--------------
--  2024-01-16 11:17:23  | 2024-01-16 11:19:11   | 2024-01-16 |        10.08
--  2024-01-16 11:40:32  | 2024-01-16 11:45:49   | 2024-01-16 |         11.2
--  2024-01-16 11:04:49  | 2024-01-16 11:10:55   | 2024-01-16 |        15.12
--  2024-01-16 11:27:03  | 2024-01-16 11:31:06   | 2024-01-16 |          9.8
--  2024-01-16 11:45:05  | 2024-01-16 12:07:12   | 2024-01-16 |        28.56 ...
```

## 7. Count the number of taxi trips by day using Group By

```sql
select cast(tpep_pickup_datetime as date) as "Day",
count(1) as "Count"
from yellow_taxi_data
group by cast(tpep_pickup_datetime as date)
order by "Count" desc;

--     Day     | Count  
-- ------------+--------
--  2024-01-27 | 110515
--  2024-01-17 | 110365
--  2024-01-18 | 110358
--  2024-01-25 | 110318
--  2024-01-20 | 108768...
```

## 8. Find max values: amount paid and nr of passengers

```sql 
select
    cast(tpep_pickup_datetime as date) as "Day",
    "DOLocationID",
    count(1) as "Count",
    max(total_amount),
    max(passenger_count)
from yellow_taxi_data
group by 1, 2 -- SQL is 1-indexed. The first argument is 1, not 0.
order by "Count" desc;

--     Day     | DOLocationID | Count |   max   | max 
-- ------------+--------------+-------+---------+-----
--  2024-01-18 |          236 |  5877 |  123.68 |   6
--  2024-01-17 |          236 |  5766 |  247.48 |   6
--  2024-01-25 |          236 |  5758 |  113.47 |   6
--  2024-01-24 |          236 |  5738 |  131.24 |   6
--  2024-01-18 |          237 |  5680 |     150 |   6
--  2024-01-30 |          236 |  5659 |   151.2 |   6...
```

## 9. Order by day and then drop off location ID in ascending order

```sql
select
    cast(tpep_pickup_datetime as date) as "Day",
    "DOLocationID",
    count(1) as "Count",
    max(total_amount)  as "Max Paid",
    max(passenger_count)  as "Max Passenger Count"
from yellow_taxi_data
group by 1, 2
order by
    "Day" asc,
    "DOLocationID" asc;

--     Day     | DOLocationID | Count | Max Paid | Max Passenger Count 
-- ------------+--------------+-------+----------+---------------------
--  2002-12-31 |          170 |     2 |     10.5 |                   1
--  2009-01-01 |          264 |     3 |    68.29 |                   2
--  2023-12-31 |           68 |     1 |     10.1 |                   2
--  2023-12-31 |          137 |     1 |    18.84 |                   2
--  2023-12-31 |          142 |     1 |     21.6 |                   2
--  2023-12-31 |          170 |     1 |    18.75 |                   2
--  2023-12-31 |          211 |     1 |    12.96 |                   1
--  2023-12-31 |          217 |     1 |    42.35 |                   6
```


# GCP

# Terraform

# Environment Setup

# Homework
