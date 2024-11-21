
# Analytics Engineering

## Prerequisites

1. a running warehouse (BigQuery or postgres)
2. a set of running pipelines ingesting the project dataset (week 3 completed)

    The following datasets ingested from the course [Datasets list](https://github.com/DataTalksClub/nyc-tlc-data/):
    - Yellow taxi data - Years 2019 and 2020
    - Green taxi data - Years 2019 and 2020
    - fhv data - Year 2019.

    <i>Note</i> that there are two ways available to load data files quicker directly to GCS, without Airflow: [option 1](https://www.youtube.com/watch?v=Mork172sK_c&list=PLaNLNpjZpzwgneiI-Gl8df8GCsPYp_6Bs) and [option 2](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse/extras) via [web_to_gcs.py script](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/03-data-warehouse/extras/web_to_gcs.py).

    However, if you've completed modules 1-3, the above data should be alreadybe found in your BigQuery account.