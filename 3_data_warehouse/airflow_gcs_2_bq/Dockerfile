# Start with the latest Airflow image (substitute `2.4.1` with the latest version)
FROM apache/airflow:2.7.2  

# Set up environment variables
ENV AIRFLOW_HOME=/opt/airflow
ARG CLOUD_SDK_VERSION=430.0.0

ENV GCLOUD_HOME=/home/google-cloud-sdk
ENV PATH="${GCLOUD_HOME}/bin:${PATH}"

# Use root user for installations
USER root

# Update package manager and install vim (and optional git, gcc, and g++)
RUN apt-get update -qq && \
    apt-get install -y vim -qq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch to airflow user
USER ${AIRFLOW_UID}

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt


# Download and install Google Cloud SDK
USER root

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

RUN DOWNLOAD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/google-cloud-sdk.tar.gz" \
    && mkdir -p "${GCLOUD_HOME}" \
    && tar xzf "${TMP_DIR}/google-cloud-sdk.tar.gz" -C "${GCLOUD_HOME}" --strip-components=1 \
    && "${GCLOUD_HOME}/install.sh" \
       --bash-completion=false \
       --path-update=false \
       --usage-reporting=false \
       --quiet \
    && rm -rf "${TMP_DIR}" \
    && gcloud --version

# Set working directory and switch back to airflow user
WORKDIR $AIRFLOW_HOME
USER $AIRFLOW_UID