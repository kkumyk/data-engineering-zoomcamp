FROM apache/airflow:2.2.0-python3.8

USER root
RUN apt-get update -qq && \
    apt-get install -y wget && \
    apt-get install -y postgresql-client && \
    apt-get install vim -qqq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

#COPY requirements.txt .
RUN pip install --no-cache-dir \
    'apache-airflow-providers-postgres==2.1.0' \
    'apache-airflow-providers-http==2.1.0'

COPY dags/ /opt/airflow/dags/
COPY requirements.txt /opt/airflow/requirements.txt

RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

ENTRYPOINT ["./scripts/entrypoint.sh"]
CMD ["--help"]