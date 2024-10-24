# First-time build can take upto 10 mins.

FROM apache/airflow:2.10.2

ENV AIRFLOW_HOME=/opt/airflow

# Ensure you are running as root
USER root 
# Install system dependencies
RUN apt-get update -qq && apt-get install vim curl -qqq

# Install setuptools globally as root to avoid permission issues
RUN python -m pip install --upgrade setuptools

# Install Poetry (as root)
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 - && \
    ln -s /etc/poetry/bin/poetry /usr/local/bin/poetry

# Set environment variables from the .env file
COPY .env /opt/airflow/.env
RUN export $(grep -v '^#' /opt/airflow/.env | xargs)

# Switch to the Airflow user by using AIRFLOW_UID
USER $AIRFLOW_UID

# Copy the Poetry configuration and install dependencies as airflow user
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-root

# Copy the rest of your project files (optional)
COPY . .

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

# ARG CLOUD_SDK_VERSION=322.0.0
# ENV GCLOUD_HOME=/home/google-cloud-sdk

# ENV PATH="${GCLOUD_HOME}/bin/:${PATH}"

# RUN DOWNLOAD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz" \
#     && TMP_DIR="$(mktemp -d)" \
#     && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/google-cloud-sdk.tar.gz" \
#     && mkdir -p "${GCLOUD_HOME}" \
#     && tar xzf "${TMP_DIR}/google-cloud-sdk.tar.gz" -C "${GCLOUD_HOME}" --strip-components=1 \
#     && "${GCLOUD_HOME}/install.sh" \
#        --bash-completion=false \
#        --path-update=false \
#        --usage-reporting=false \
#        --quiet \
#     && rm -rf "${TMP_DIR}" \
#     && gcloud --version

WORKDIR $AIRFLOW_HOME

# USER $AIRFLOW_UIDSetting up Airflow with Docker

