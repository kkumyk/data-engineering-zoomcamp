# Module 5: Batch Processing

## Introduction to Batch Processing
There are 2 ways of processing data:
- Batch processing: processing chunks of data at regular intervals; e.g.: processing taxi trips each month.
- Streaming: processing data on the fly; e.g.: processing taxi trips data as soon as it is generated.

### Batch Jobs
A Batch Job is a unit of work that will process data in batches.

BJs can be scheduled in many ways: weekly, daily, hourly...

BJs can be carry out using different technologies:

  - Python scripts
  - SQL
  - Spark which will be used in this lesson

BJs are commonly orchestrated with tools such as Airflow.


## Introduction to Apache Spark

- an open-source multi-language unified analytics engine for large-scale data processing;
- is an engine because it processes data;
- can be run in clusters with multiple nodes each pulling and transforming data;
- Java and Scala natively, and there are wrappers for Python, R and other languages;
- the wrapper for Python is called PySpark;
- can deal with both batches and streaming data;

## Why Do We Need Spark?

Spark is used for transforming data in a Data Lake.

There are tools such as Hive, Presto or Athena (a AWS managed Presto) that allow you to express jobs as SQL queries. However, there are times where you need to apply more complex manipulation which are very difficult or even impossible to express with SQL (such as ML models); in those instances, Spark is the tool to use.

For everything that can be expressed with SQL, it's always a good idea to do so, but for everything else, there's Spark.

## [Spark Installation on Linux](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/05-batch/setup/linux.md)

### Installing [OpenJDK](https://jdk.java.net/archive/) (Java Development Kit) 17 

- I was not able to install version 11 on Ubuntu 23.10 but I see that Spark now also supports 17.
```bash
# download version 17
wget https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz

# unpack it
tar xzfv openjdk-17.0.2_linux-x64_bin.tar.gz

# verify that the java binary exists
ls ~/spark/jdk-17.0.2/bin/java

#if the java executable is found, proceed to set the JAVA_HOME and update/add it to PATH;
# once the JDK is correctly installed, update the environment variables in your shell configuration file (~/.bashrc, ~/.zshrc, etc.)
export JAVA_HOME="${HOME}/spark/jdk-17.0.2"
export PATH="${JAVA_HOME}/bin:${PATH}"

# source the file to apply the changes
source ~/.bashrc   # or source ~/.zshrc depending on your shell

# check Java version to see if it worked
java --version

# the above should display the version of the installed JDK; output:
openjdk 17.0.2 2022-01-18
OpenJDK Runtime Environment (build 17.0.2+8-86)
OpenJDK 64-Bit Server VM (build 17.0.2+8-86, mixed mode, sharing)

# remove the archive
rm openjdk-17.0.2_linux-x64_bin.tar.gz
```

### Installing Spark

```bash
# download Spark 3.3.2 version:
wget https://archive.apache.org/dist/spark/spark-3.5.3/spark-3.5.3-bin-hadoop3.tgz

# unpack
tar xzfv spark-3.5.3-bin-hadoop3.tgz

# remove the archive
rm spark-3.5.3-bin-hadoop3.tgz

# add it to PATH
export SPARK_HOME="${HOME}/spark/spark-3.5.3-bin-hadoop3"
export PATH="${SPARK_HOME}/bin:${PATH}"

# check if Spark is working with $ spark-shell and run the following:
val data = 1 to 10000
val distData = sc.parallelize(data)
distData.filter(_ < 10).collect()
```

### PySpark

```bash
# To run PySpark, we first need to add it to PYTHONPATH:
export PYTHONPATH="${SPARK_HOME}/python/:$PYTHONPATH"
export PYTHONPATH="${SPARK_HOME}/python/lib/py4j-0.10.9.7-src.zip:$PYTHONPATH"

# run Jupyter to test if things work by going to a different directory and downloading a CSV file for testing:
wget https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
```





## Spark SQL and DataFrames

Spark SQL - one way of querying our Spark data frame

- Spark Cluster
- Cluster Manager

- used Jupyter Notebooks for reading csv files (our taxi data) into Spark data frames
  
### DataFrame Functions
- two types:
  - Actions
    - execute right away
  - Transformations
    - lazy – they do not get executed straight away

## Spark Internals

## Running Spark in the Cloud

## Credits
- [DataTalksClub](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/05-batch)
- [Notes by Alvaro Navas](https://github.com/ziritrion/dataeng-zoomcamp/blob/main/notes/5_batch_processing.md)
- [Week 5: DE Zoomcamp 5.2.1 – Installing Spark on Linux](https://learningdataengineering540969211.wordpress.com/tag/dezoomcamp/)
- [Notes by HongWei](https://github.com/hwchua0209/data-engineering-zoomcamp-submission/blob/main/05-batch-processing/README.md)
- [2024 videos transcript by Maria Fisher](https://drive.google.com/drive/folders/1XMmP4H5AMm1qCfMFxc_hqaPGw31KIVcb)
- [What is .bashrc file in Linux?](https://www.digitalocean.com/community/tutorials/bashrc-file-in-linux)