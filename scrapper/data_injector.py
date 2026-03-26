from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.dialects.postgresql import insert                         
import sys
import csv
import json
import pandas as pd


def insert_to_db(car, conn):
    try:
        insert_statement = insert(cars_raw).values(id=car['ID'], url=car['URL'], price=car['price'], model=car['model'], brand=car['brand']).on_conflict_do_nothing(index_elements=['id'])
        conn.execute(insert_statement)
    except ValueError:
        print(f"Invalid listing (bad price: {car['price']}), skipping ID {car['ID']}")
    return



engine = create_engine('postgresql://admin:admin@localhost:5432/autopred', echo = True)

meta = MetaData()

cars_raw = Table(
    "cars_raw",
    meta,
    Column('id', Integer, primary_key = True),
    Column('url', String),
    Column('price', Integer),
    Column('model', String),
    Column('brand', String)
)       

meta.create_all(engine)

endpoint = sys.argv[1]

cars_raw_df = pd.read_csv(endpoint + '/car_data_' + endpoint + '.csv')            

cars_raw_df['ID'] = pd.to_numeric(cars_raw_df['ID'], errors='coerce')
cars_raw_df.dropna(subset=['ID'], inplace=True)
cars_raw_df['ID'] = cars_raw_df['ID'].astype(int)

cars_raw_df.drop_duplicates(['ID'], inplace=True)

cars_raw_df['price'] = pd.to_numeric(cars_raw_df['price'], errors='coerce')
cars_raw_df.dropna(subset=['price'], inplace=True)
cars_raw_df['price'] = cars_raw_df['price'].astype(int)

with engine.begin() as conn:
    cars_raw_df.apply(lambda row: insert_to_db(row, conn), axis=1)
    
        
            




