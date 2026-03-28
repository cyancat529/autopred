from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, Date
from sqlalchemy.dialects.postgresql import insert
import requests
import pandas as pd
import datetime
import os
import sys

# FUNCTIONS

def insert_to_db(car, conn, cars_raw_table):
    try:
        insert_statement = insert(cars_raw_table).values(
            id=car['ID'],
            url=car['URL'],
            brand=car['brand'],
            model=car['model'],
            year=car['year'],
            mileage=car['mileage'],
            power=car['power'],
            price=car['price'],
            seats=car['seats'],
            fixed_price=car['fixed_price'],
            fuel=car['fuel'],
            color=car['color'],
            registered=car['registered'],
            dmfw=car['DMFW'],
            origin=car['origin'],
            country_origin=car['country_origin'],
            date_posted=car['date_posted'],
            emmision=car['emission'],
            transmission=car['transmission'],
            bodywork=car['bodywork']
        ).on_conflict_do_nothing(index_elements=['id'])
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
    Column('id', Integer, primary_key=True),
    Column('url', String),
    Column('brand', String),
    Column('model', String),
    Column('year', Integer),
    Column('mileage', Integer),
    Column('power', Integer),
    Column('price', Integer),
    Column('seats', Integer),
    Column('fixed_price', Boolean),
    Column('fuel', String),
    Column('color', String),
    Column('registered', String),
    Column('dmfw', String),
    Column('origin', String),
    Column('country_origin', String),
    Column('date_posted', Date),
    Column('emmision', String),
    Column('transmission', String),
    Column('bodywork', String)
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

cars_raw_df['year'] = pd.to_numeric(cars_raw_df['year'].str.replace('.', '', regex=False), errors='coerce').astype('Int64')
cars_raw_df['mileage'] = pd.to_numeric(cars_raw_df['mileage'], errors='coerce').astype('Int64')
cars_raw_df['power'] = pd.to_numeric(cars_raw_df['power'], errors='coerce').astype('Int64')
cars_raw_df['seats'] = pd.to_numeric(cars_raw_df['seats'].str.extract(r'(\d+)')[0], errors='coerce').astype('Int64')
cars_raw_df['fixed_price'] = cars_raw_df['fixed_price'].map({'DA': True, 'NE': False})
cars_raw_df['date_posted'] = pd.to_datetime(cars_raw_df['date_posted'].str.strip('.'), format='%d.%m.%Y', errors='coerce')

cars_raw_df['mileage'] = cars_raw_df['mileage'].fillna(0)

# Step 7: Database Insertion
with engine.begin() as conn:
    cars_raw_df.apply(lambda row: insert_to_db(row, conn, cars_raw_table), axis=1)
    
        
            




