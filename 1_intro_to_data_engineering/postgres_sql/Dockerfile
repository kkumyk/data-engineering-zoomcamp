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
COPY zones.csv zones.csv

# define what to do first when the container runs
# in this example, we will just run the script
ENTRYPOINT [ "python", "ingest_data.py" ]