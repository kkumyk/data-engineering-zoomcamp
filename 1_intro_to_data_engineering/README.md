
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
Job finished successfully! Celebrate it with 10 pizzas!
```

## 2. Running Postgres in a Docker Container

[video source: 1.2.2](https://www.youtube.com/watch?v=2JM-ziJt0WI&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=5)

<i>mounting</i> - mapping of a folder on the host machine to a folder in a Docker container

### Creating a Postgres database

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

#### Issue encountered:
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

### Testing the connection

Once the container is running, we can log into our database using the following command:
```bash
psql -h localhost -U your_user_name -d ny_taxi
```
- <i>ny_taxi</i> is the name of the database we created with the command from the previous section. 
- The password will be requested after running the command above (the one set with the command from the previous section).

<br>
<hr>


# GCP

# Terraform

# Environment Setup

# Homework
