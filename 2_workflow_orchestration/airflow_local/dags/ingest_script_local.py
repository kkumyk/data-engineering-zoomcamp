import logging 

from time import time
import pandas as pd
from sqlalchemy import create_engine


#set up logging
logger = logging.getLogger(__name__)

def ingest_callable(user, password, host, port, db, table_name, csv_file):
    print(table_name, csv_file)

    logger.info("Table name and csv file are %s, %s", table_name, csv_file)
    logger.info("User, password, host, port, db are %s, %s, %s, %s, %s", user, password, host, port, db)
    
    #connect to postgres db
    logger.info("Connecting to db")
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()
    logger.info('Connection established successfully, inserting data...')

    #import entire csv dataset as an iterator
    t_start = time()
    df_iter = pd.read_csv(csv_file, iterator=True, chunksize=100000)

    df = next(df_iter)

    if 'tpep_dropoff_datetime' in df.columns:
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    else:
        logger.info("No column called tpep_dropoff_datetime")

    if 'tpep_pickup_datetime' in df.columns:
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    else:
        logger.info("No column called tpep_pickup_datetime")

    #create a new table in postgres with only the header information. This table will not contain any data rows yet
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='append')

    #now insert all the rows of the first chunk of dataset into the postgres table
    df.to_sql(name=table_name, con=engine, if_exists='append')

    t_end = time()

    logger.info('Inserted first chunk')
    print(f'Took {float(t_end - t_start):.3f} seconds')

    #Repeat for all chunks until no more chunks left
    while True:
        t_start = time()

        try:
            df = next(df_iter)
        except StopIteration:
            logger.info('Completed.')
            break
        
        if 'tpep_dropoff_datetime' in df.columns:
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        else:
            logger.info("No column called tpep_dropoff_datetime")

        if 'tpep_pickup_datetime' in df.columns:
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        else:
            logger.info("No column called tpep_pickup_datetime")

        logger.info('Inserting next chunk')
        df.to_sql(name=table_name, con=engine, if_exists='append')

        t_end = time()

        logger.info('Inserted another chunk')
        print(f'Took {float(t_end - t_start):.3f} seconds')