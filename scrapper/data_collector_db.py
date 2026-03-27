from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.dialects.postgresql import insert                         
import requests
import pandas as pd
import datetime
import os
import sys

# FUNCTIONS

def insert_to_db(car, conn, cars_raw_table):
    try:
        insert_statement = insert(cars_raw_table).values(id=car['ID'], url=car['URL'], price=car['price'], model=car['model'], brand=car['brand']).on_conflict_do_nothing(index_elements=['id'])
        conn.execute(insert_statement)
    except ValueError:
        print(f"Invalid listing (bad price: {car['price']}), skipping ID {car['ID']}")
    return


# Step 1: Fetch data from API

url = "http://localhost:5000/get_page/"   # replace with your API endpoint
dt = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
fin_page = int(sys.argv[1])

try:
    os.makedirs(dt, exist_ok=True)
    print(f"Directory '{dt}' created or already exists.")
except OSError as e:
    print(f"Error creating directory: {e}")

cars = []

for i in range(1,fin_page + 1):
    response = requests.get(url+str(i))                                 
    data = response.json()   

    # Step 2: Convert response to JSON
    data = response.json()

    # Step 3: Normalize JSON into a flat table (if nested)
    df = pd.json_normalize(data)

    # Step 4: Save to CSV
    cars.append(df)
    print(f'Page {i} finished')

cars_raw_df = pd.concat(cars, ignore_index=True)

# Step 5: Initialize DB Connection

engine = create_engine('postgresql://admin:admin@db:5432/autopred', echo = True)

meta = MetaData()

cars_raw_table = Table(
    "cars_raw",
    meta,
    Column('id', Integer, primary_key = True),
    Column('url', String),
    Column('price', Integer),
    Column('model', String),
    Column('brand', String)
)       

meta.create_all(engine)

# Step 6: Data Cleaning

cars_raw_df['ID'] = pd.to_numeric(cars_raw_df['ID'], errors='coerce')
cars_raw_df.dropna(subset=['ID'], inplace=True)
cars_raw_df['ID'] = cars_raw_df['ID'].astype(int)

cars_raw_df.drop_duplicates(['ID'], inplace=True)

cars_raw_df['price'] = pd.to_numeric(cars_raw_df['price'], errors='coerce')
cars_raw_df.dropna(subset=['price'], inplace=True)
cars_raw_df['price'] = cars_raw_df['price'].astype(int)

# Step 7: Database Insertion
with engine.begin() as conn:
    cars_raw_df.apply(lambda row: insert_to_db(row, conn, cars_raw_table), axis=1)
    
        
            




