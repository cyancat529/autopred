import requests
import pandas as pd
import datetime
import os
import sys

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

    # Step 2: Convert response to JSON
    data = response.json()

    # Step 3: Normalize JSON into a flat table (if nested)
    df = pd.json_normalize(data)

    # Step 4: Save to CSV
    cars.append(df)
    print(f'Page {i} finished')

df = pd.concat(cars, ignore_index=True)
df.to_csv(f'{dt}/car_data_{dt}.csv', index=False)
print("Data saved to output.csv")
