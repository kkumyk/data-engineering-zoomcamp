Table of Contents:

[Introduction to Data Engineering](#1-creating-a-custom-pipeline-with-dockerintroduction-to-data-engineering)

[Docker & Postgres](#docker--postgres)

[Creating a Custom Pipeline with Docker](#creating-a-custom-pipeline-with-docker)

[Running Postgres in a Docker Container](#2-running-postgres-in-a-docker-container)

[Ingesting NY Trips Data to Postgres DB with Python](#3-ingesting-ny-trips-data-to-postgres-db-with-python)

[Connecting pgAdmin and Postgres with Docker](#4-connecting-pgadmin-and-postgres-with-docker)

[Putting the Ingestion Script ingest_data.py into Docker Container](#5-putting-the-ingestion-script-ingest_datapy-into-docker-container)

[Running Postgres and pgAdmin with docker-compose.yaml](#6-running-postgres-and-pgadmin-with-docker-composeyaml)


[Docker Networking and Port Mapping](#docker-networking-and-port-mapping)

[SQL Refresher](#sql-refresher)

[Terraform and Google Cloud Platform](#terraform-and-google-cloud-platform)

# Introduction to Data Engineering

Data Engineering is the design and development of systems for collecting, storing and analyzing data at scale.

## Docker & Postgres

### Creating a custom pipeline with Docker

To build the image:

```bash
docker build -t install_poetry_image_test:poetry .
```

- install_poetry_image_test will be the name of the image
- the image tag will be poetry

Run the container and pass an argument to it, so that our pipeline will receive it:
```bash
docker run -it install_poetry_image_test:poetry 5

# Expected result:
# ['pipeline.py', '5']
# Job finished successfully! Celebrate it with 5 pizzas!
```

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

### Issues Encountered:
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
    - Under General give the Server a name, e.g.: Docker localhost 
    - Under Connection add the same host name, user and password you used when running your Postgres container.
    - Host name/address will be the name specified in the command for running the Postgres container. Same for the user name.
    - After saving the configurations, you should be connected to the database.
    - Create yellow_taxi_data table and run ingest_data.py script on parquet and csv files to add taxi and zones data to the Postgres database. See instructions in the section 3.

## 5. Putting the Ingestion Script ingest_data.py into Docker Container

[video source: 1.2.4](https://www.youtube.com/watch?v=B1WwATwf-vY&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=8)

### Issues Encountered:
### 1. Was not able to build the image.
```bash
8.471 Note: This error originates from the build backend, and is likely not a problem with poetry but with psycopg2 (2.9.9) not supporting PEP 517 builds.
You can verify this by running 'pip wheel --no-cache-dir --use-pep517 "psycopg2 (==2.9.9)"'.
```
To solve the error above, psycopg2 was replaced with psycopg2-binary. 

### 2. The Docker container could not see the Parquet file.
The yellow taxi data was not downloaded by providing the URL. The Parquet file was downloaded and saved to the same directory as the Dockerfile.
The Dockerfile needed to be adjusted so that the input file is copied to the container as well:

```bash
COPY yellow_tripdata.parquet yellow_tripdata.parquet 
```

Once the above issues were resolved:

1. Amend the Dockerfile as per tutorial and build the image:

Dockerfile:

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
COPY ingest_data.py ingest_data.py

# Copy the Parquet file into the container
COPY yellow_tripdata.parquet yellow_tripdata.parquet

# define what to do first when the container runs
# in this example, we will just run the script
ENTRYPOINT [ "python", "ingest_data.py" ]
```

```bash
docker build -t taxi_ingest:v001 .
```

2. Run Postgres in a Docker container:

```bash
docker run -it \
    -e POSTGRES_USER="your_user_name" \
    -e POSTGRES_PASSWORD="your_db_password" \
    -e POSTGRES_DB="ny_taxi" \
    -v ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
        --network=pg-network \
        --name pg_container_name \ 
    postgres:15
```

3. Add the ingestion script to the running Docker container:

```bash
docker run -it \
    --network=pg-network \
    taxi_ingest:v001 \
    --user=your_user_name \
    --password=your_db_password \
    # the same as specified as the name in the previous command when running the Postgres:
    --host=pg_container_name \ 
    --port=5432 \
    --db=ny_taxi \
    --tb=yellow_taxi_trips \
    --url="yellow_tripdata.parquet"
```

4. In Docker Desktop run the pgadmin container and add the newly created server etc, view the ingested data. 

## 6. Running Postgres and pgAdmin with docker-compose.yaml
[video source: 1.2.5](https://www.youtube.com/watch?v=hKI6PkPhpa0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=8)

In section 4 we made two containers talk to each other via the same network. This was done by running two command line commands. In this section we replace that process with a yaml file that will contain the instructions for the same process to happen from a single source.

1. Add docker-compose.yaml file.

```yaml
services:
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=your_user
      - POSTGRES_PASSWORD=your_password
      - POSTGRES_DB=ny_taxi
    volumes:
      - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    ports:
      - "5432:5432"
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    volumes:
      - "./data_pgadmin:/var/lib/pgadmin"
    ports:
      - "8080:80"
```

2. Create data_pgadmin folder on the same level as the ny_taxi_postgres_data folder which is also where your docker compose file was saved.

3. Make sure any previous Docker containers are not running:

```bash
docker ps -a
```
4. Run docker compose:
```bash
docker-compose up
```
5. Login in to your pgadmin in your browser and configure a new server.

- The Host name/address will be the name you gave to your Postgres service in your docker-compose file: <i>pgdatabase</i>

6. Now that the Postgres and pgadmin containers are running, we need to populate it with the data:

- Build the Docker image for the ingestion script:
```bash
docker build -t taxi_ingest:v001 .
```
- If you want to re-run the dockerized ingest script when you run Postgres and pgAdmin with docker-compose, you will have to find the name of the virtual network that Docker compose created for the containers.
- For this, use the command docker network ls to find it and then change the docker run command for the dockerized script to include the network name:

```bash
docker network ls
# e.g.: postgres_sql_default

docker run -it \
# the name of the virtual network that Docker compose created for the containers
    --network=postgres_sql_default \
    taxi_ingest:v001 \
    --user=your_user \
    --password=your_password \
    --host=pgdatabase \ # == name of Postgres service in docker-compose:
    --port=5432 \
    --db=ny_taxi \
    --tb=yellow_taxi_trips \
    --url="yellow_tripdata.parquet"

docker run -it \
# the name of the virtual network that Docker compose created for the containers
    --network=postgres_sql_default \
    taxi_ingest:v001 \
    --user=your_user \
    --password=your_password \
    --host=pgdatabase \ # == name of Postgres service in docker-compose:
    --port=5432 \
    --db=ny_taxi \
    --tb=zones \
    --url="zones.csv"
```
You should now see two tables in your pgadmin.
<br>
<hr>

# Docker Networking and Port Mapping
[video source: 1.5.1](https://www.youtube.com/watch?v=tOr4hTsHOzU)

Host: Ubuntu (ports: 5432, 8080)

    Two containers are sharing the same network (postgres_sql_default):
        - container 1: pgdatabase (port 5432)
        - container 2: pgadmin (port 80)

Within this network both containers are accessible to each other and pgadmin cn talk to Postgres.

In docker-compose file the line "5432:5432" means that we map the port on the computer to the port on the container. If Postgres is already running when we are trying to run docker-compose if will through an error as the port is already taken. To overcome this error, we can do port forwarding by mapping the localhost port 5431 to port on the Docker container: "5431:5432".

If we want to run the ingestion script after the port mapping, we don't need to do this for the ingestion script as it talks directly to the container on port 5432.

</br>
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

# Terraform and Google Cloud Platform
[video source: 1.3.1](https://www.youtube.com/watch?v=Hajwnmj0xfQ&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=7)

[Terraform](https://www.terraform.io/) is an [IAC (Infrastructure-as-Code)](https://www.wikiwand.com/en/articles/Infrastructure_as_code) tool. It allows to provide infrastructure resources as code. The infrastructure is handled as an additional software component and can be version controlled. It can be described as git version control but for infrastructure. As a result, no need to use cloud providers' GUIs. In short, this is a tool that helps you to mange the infrastructure lifecycle.

On of the main advantages is a state-based approach to track resource changes throughout deployments.

## Local Setup for GCP

GCP is organised around projects. From this project you can have access to all available GCP resources and services from this project's dashboard.

Next, we are going to create a project, a service account and download authentication keys to our computer.

 A <i>service account</i> is like a user account but for apps and workloads; you may authorize or limit what resources are available to your apps with service accounts.

1. Create an account on GCP. You will receive $300 in credit when signing up for the first time.
2. Setup a new project and write down the Project ID.
    - From the GCP Dashboard, click on the drop down menu next to the Google Cloud Platform title to show the project list and click on <i>New project</i>".
    - Name your project, e.g.: <i>dtc-de</i>. You can use the autogenerated Project ID or re-generate to make sure that this ID is unique to all of GCP environment. Leave the organization as <i>No organization</i>. Click on <i>Create</i>.
    <!--Project ID: dtc-de-course-438317-d4 -->
    - Back on the dashboard, make sure that your project is selected. Click on the previous drop down menu to select it otherwise.

3. To create a Service Account for project "dtc-de" go to:
    - IAM & Admin > Service Accounts > + create service account
    - Provide service account details: name (e.g.: dtc-de-user), user (name + project's email address)
    - Grant this service account access to project: Basic > Viewer > Continue > Done

4. Download auth-key(.json)
    - From the dashboard of the Service Accounts go to Actions > Manage Keys > Add key > Create new key > JSON > Create > The key will be downloaded to your computer.
5. Download [Google Cloud SDK incl. Google Cloud CLI for local setup](https://cloud.google.com/sdk/docs/install-sdk)
    - Follow the instructions to install and connect to your account and project.
    - Check if already installed: <i>gcloud -v</i>. 
    This step completes the Google Cloud installation.

6. Set env var to point to your downloaded GCP auth-key:
    - Go to your Downloads folder where the key was saved and on the command line run the command below:
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="path/to/auth/key.json"
    ```
7. Refresh token, verify authentication:
    ```bash
    gcloud auth application-default login 
    ```
    Press <i>yes</i> to continue and authenticate in the browser (choose email and allow it). End of authentication with the Cloud SDK meaning your local setup is now authenticated with the cloud environment.

You should now be ready to work with GCP.
<hr>

## GCP Access Setup

### Project Infrastructure Modules in GCP:

- Google Cloud Storage (GCP): Data Lake where the data will be stored
- BigQuery: Data Warehouse provides a more structured way to access the data stored in the data lake

In the upcoming parts of this course we are going to setup a data lake on Google Cloud Storage and a warehouse in BigQuery. 

We need to setup access first by assigning the Storage Admin, Storage Object Admin, BigQuery Admin and Viewer IAM roles to the Service Account, and then enable the IAM and IAM Credentials APIs for our project:

1. IAM Roles for Service account (Storage Admin, Storage Object Admin, BigQuery Admin, Viewer):

    Now that our local env is authenticated with Google Cloud, we need to add permissions for our service account.
    
    From GCP dashboard go to IAM and edit permissions for the last service account by clicking on the pencil shaped icon on the left:
    - Select role > Storage Admin
        - for creating and managing buckets
    - Add another role > Storage Object Admin
        - for creating and managing objects within the buckets
    - Add another role > BigQuery Admin
        - for managing BigQuery resources and data 
        
        Click <i>Save</i>

2. Enable Identify and Access Management (IAM) and IAM Credentials APIs:
    - https://console.cloud.google.com/apis/library/iam.googleapis.com
    - https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com

    ! On the GCP dashboard, make sure to select the right project while enabling these APIs for (in case when having multiple projects).

    When the local env interacts with the cloud it does not do it directly with the resource. The above APIs enable this communication.

3. Make sure that the GOOGLE_APPLICATION_CREDENTIALS environment variable is set by running the command below:
    ```bash
    gcloud auth application-default login
    ```
<hr>

## Terraform Basics
[video source 1.3.2](https://www.youtube.com/watch?v=dNkEgO-CExg&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=11)

Download Terraform client from https://developer.hashicorp.com/terraform/install

### Terraform Components:
1. the code files
2. Terraform commands

### Terraform Configuration:
- the set of files used to describe infrastructure in Terraform
- T. config files end up in .tf for files written in Terraform language or tf.json for JSON files
- a T. config must be in its own working directory
- you cannot have 2 or more separate configurations in the same folder.

Example of a basic main.tf file written in Terraform language to describe basic infrastructure:

```bash
terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "3.5.0"
    }
  }
}

provider "google" {
  credentials = file("<NAME>.json")

  project = "<PROJECT_ID>"
  region  = "us-central1"
  zone    = "us-central1-c"
}

resource "google_compute_network" "vpc_network" {
  name = "terraform-network"
}

```

- Terraform divides information into blocks, which are defined within braces ({}); statements are not required to end with a semicolon ; but use line breaks instead.
- Arguments with single-line values in the same nesting level have their equal signs (=) aligned for easier reading.
- There are 3 main blocks:
    1. the <strong>terraform</strong> block - only one should be specified
        - includes required_providers sub-block with the provider(s) required by the configuration
    2. the <strong>provider</strong> block - multiple instances can be specified
        - A provider is a plugin that Terraform uses to create and manage resources.
        - Each provider needs a source in order to install the right plugin. By default the Hashicorp repository is used, in a similar way to Docker images.
    hashicorp/google is short for registry.terraform.io/hashicorp/google .
    Optionally, a provider can have an enforced version. If this is not specified the latest version will be used by default, which could introduce breaking changes in some rare cases.

    - The provider block configures a specific provider. Since we only have a single provider, there's only a single provider block for the google provider.
    The contents of a provider block are provider-specific. The contents in this example are meant for GCP but may be different for AWS or Azure.
    3. the <strong>resource</strong> block - multiple instances can be specified
        - defines the actual components of our infrastructure
        - has 2 strings before the block which create the resource ID in the format of type.name:
            1. the resource type
            2. the resource name

        - Resource names are the internal names that we use in our Terraform configurations to refer to each resource and have no impact on the actual infrastructure.
        - 
            Do not confuse the resource name with the name argument!

### Terraform Execution Commands:

```bash
# refresh service account auth token for this session
gcloud auth application-default login

# initialize state file (.tfstate)
# initialize your work directory by downloading the necessary providers/plugins
terraform init 

# formats your configuration files so that the format is consistent
terraform fmt (optional)

# returns a success message if the configuration is valid and no errors are apparent
terraform validate (optional)

# check changes to new infra plan:
# creates a preview of the changes to be applied against a remote state,
# allowing you to review the changes before applying them
terraform plan -var= "project=YOUR_PROJECT_ID"

# create new infra / applies the changes to the infrastructure
terraform apply -var="YOUR_PROJECT_ID"

# removes your stack from the infrastructure:
# delete infra after work completion to avoid costs of any running services
terraform destroy
```

## Creating GCP Project Infrastructure with Terraform
[video resource 1.3.2](https://www.youtube.com/watch?v=dNkEgO-CExg&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=11)

### Prerequisites
#### Terraform Installation on Linux/Ubuntu
```bash
# cd to the folder with the saved binary files
cd Downloads/

# identify the right path to move the files to
echo $PATH

# add terraform to path
mv /tmp/terraform ~/.local/bin/
ls -l ~/.local/bin/
```


1. Create two files that will include all the blocks we need for our GCP project:
    - <b>main.tf</b> - here we specify the following terraform block:

        ```bash
        terraform {
        required_version = ">= 1.0"
        backend "local" {}
        required_providers {
            google = {
            source  = "hashicorp/google"
            }
        }
        }
        ```

        - The <i>required_version</i> field states the minimum Terraform version to be used.
        - The  <i>backend</i> field states where we would like to store the state of the infrastructure.
            - <i>local</i> means that we will store it locally in our computers. Alternatively, you could store the state online.
        - The <i>provider</i> will not make use of the credentials field because when we set up GCP access we already created a GOOGLE_APPLICATION_CREDENTIALS env-var which Terraform can read in order to get our authentication keys.


    - <b>variables.tf</b> - here we will store variables that may change depending on your needs and location. 
        
        The ones to note are:

        - <i>region</i> may vary depending on your geographical location; change it according to your needs.
        - <i>BQ_DATASET</i> has the name of the table for BigQuery. You may leave it as it is or change it to fit your needs.
        - <i>project</i> is the Project ID of your project in GCP. Since the ID is unique, it is good practice to have Terraform as for it every time in case the same code is applied on different projects.

    The infrastructure we will need consists of a:
    - Cloud Storage Bucket (google_storage-bucket) for our Data Lake
    - BigQuery Dataset (google_bigquery_dataset)

Copy the [main.tf](https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/1_intro_to_data_engineering/terraform/main.tf) and [variables.tf](https://github.com/kkumyk/data-engineering-zoomcamp/blob/main/1_intro_to_data_engineering/terraform/variables.tf) files to a new folder within your work directory so that the subfolder only contains the two Terraform configuration files.

2. Refresh service-account's auth-token for this session:
    ```bash
    gcloud auth application-default login
    ```
3. Initialize configuration and import plugins for Google provider:
<i>cd</i> to the folder with the Terraform config files and run the following command:
    ```bash
    terraform init
    ```
This will download the necessary plugins to connect to GCP and download them to ./.terraform. 
Add your project's ID once prompted.

4. Now let's plan the infrastructure / Create resources with Terraform plan :
    ```bash
    terraform plan
    ```
Terraform will ask for your Project ID. Type it and press enter to let Terraform access GCP and figure out what to do. The infrastructure plan will be printed on screen with all the planned changes marked with a + sign next to them.

5. Create Infra with Apply :
    ```bash
    terraform apply
    ```
You will need to confirm this step by typing yes when prompted. This will create all the necessary components in the infrastructure an return a terraform.tfstate with the current state of the infrastructure.
6. Delete infra after your work
After you've successfully created the infrastructure, you may destroy it so that it doesn't consume credit unnecessarily:
    ```bash
    terraform destroy
    ```


## Credits

Big thank you to [Alvaro Navas](https://github.com/ziritrion) for [detailed and highly structured course docs](https://github.com/ziritrion/dataeng-zoomcamp/tree/main) that were used as times there the video material was not clear.
