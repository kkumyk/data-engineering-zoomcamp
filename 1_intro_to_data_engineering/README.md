
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

    1. Servers > Register Server
    2. Under <i>General</i> give the Server a name, e.g.: Docker localhost 
    3. Under <i>Connection</i> add the same host name, user and password you used when running your Postgres container.
    4. After saving the configurations, you should be connected to the database.
    5. Create yellow_taxi_data table and run ingest_data.py script on parquet and csv files to add taxi and zones data to the Postgres database. See instructions in the section 3.

## 5. Dockerizing ingest_data.py

## 6. Running Postgres and pgAdmin with Docker-compose

In section 4 we made two containers talk to each other via the same network. This was done by running two command line commands. In this section we replace that process with a yaml file that will contain the instructions for the same process to happen from a single source.


<br>
<hr>

# SQL Refresher

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

# GCP

# Terraform

# Environment Setup

# Homework
