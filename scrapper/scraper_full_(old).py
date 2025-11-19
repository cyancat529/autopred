import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import datetime

###       polovniautomobili.com scraper
###   VERSION 2 - Individual page scrapping

base_url = 'https://www.polovniautomobili.com/auto-oglasi/pretraga?page='
cars = []
filter = '&sort=renewDate_desc&city_distance=0&showOldNew=all&without_price=1'

print(datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S"))
log = []

for page in range(1,3):
    url = f'{base_url}{page}{filter}'

    response = requests.get(url, headers={'User-Agent': 'MyScraper'})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    listings = soup.select('.ordinaryClassified')  # Multiple possible selectors

    i = 1

    for listing in listings:
        try:
            link = 'https://www.polovniautomobili.com' + listing.find_all('a', href=True)[0]['href']

            resp = requests.get(link, headers={'User-Agent': 'MyScraper'})
            resp.raise_for_status()
            car_page = BeautifulSoup(resp.text, 'html.parser')

            data = car_page.find_all(class_='uk-width-1-2 uk-text-bold')
            data1 = car_page.find_all(class_='infoBox')[1]
            data2 = data1.find_all(class_='uk-width-1-2 uk-text-bold')
            
            car = {
                'price': car_page.find_all(class_='priceClassified')[0].text[:-2],
                'brand': data[1].text,
                'model': data[2].text,
                'year': data[3].text[:-1],
                'mileage': data[4].text[:-3],
                'bodywork': data[5].text,
                'fuel': data[6].text,
                'volume': data[7].text,
                'power': data[8].text.split('/')[0],
                'ID': data[11].text,
            }        
            if(data1.find_next("div", string='Plivajući zamajac')): car['DMFW'] = data1.find_next("div", string='Plivajući zamajac').parent.find_next(class_='uk-width-1-2 uk-text-bold').text.strip('\n\t ')
            if(data1.find_next("div", string='Emisiona klasa motora')): car['emission'] = data1.find_next("div", string='Emisiona klasa motora').parent.find_next(class_='uk-width-1-2 uk-text-bold').text.strip('\n\t ')
            if(data1.find_next("div", string='Menjač')): car['transmission'] = data1.find_next("div", string='Menjač').parent.find_next(class_='uk-width-1-2 uk-text-bold').text.strip('\n\t ')
            if(data1.find_next("div", string='Broj vrata')): car['door'] = data1.find_next("div", string='Broj vrata').parent.find_next(class_='uk-width-1-2 uk-text-bold').text.strip('\n\t ')
            if(data1.find_next("div", string='Broj sedišta')): car['seats'] = data1.find_next("div", string='Broj sedišta').parent.find_next(class_='uk-width-1-2 uk-text-bold').text.strip('\n\t ')
            if(data1.find_next("div", string='Boja')): car['color'] = data1.find_next("div", string='Boja').parent.find_next(class_='uk-width-1-2 uk-text-bold').text.strip('\n\t ')
            if(data1.find_next("div", string='Registrovan do')): car['registered'] = data1.find_next("div", string='Registrovan do').parent.find_next(class_='uk-width-1-2 uk-text-bold').text.strip('\n\t ')
            if(data1.find_next("div", string='Poreklo vozila')): car['origin'] = data1.find_next("div", string='Poreklo vozila').parent.find_next(class_='uk-width-1-2 uk-text-bold').text.strip('\n\t ')
            if(data1.find_next("div", string='Zemlja uvoza')): car['country_origin'] = data1.find_next("div", string='Zemlja uvoza').parent.find_next(class_='uk-width-1-2 uk-text-bold').text.strip('\n\t ')
            car['price'] = car['price'].replace('.', '')
            car['mileage'] = car['mileage'].replace('.', '')

            cars.append(car)
            
        except Exception as error:
            # handle the exception
            print(f'{datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")} - An exception occurred: {error}')
            log.append(f'{datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")} - An exception occurred: {error}')
            car = {}
        
        print(f'{page} - {i}')
        i+=1
        #time.sleep(random.randint(0, 2)) 


df = pd.DataFrame(cars)
df.to_csv(f'car_data_{datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")}.csv', index=False, encoding='utf-8')

with open(f'log_{datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")}.csv', "a") as f:
  f.write('\n'.join(log))