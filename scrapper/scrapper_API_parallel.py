import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import datetime
import asyncio

###       polovniautomobili.com scraper
###     VERSION 3 - Updated page scrapping

class CarScrapper:
    @staticmethod
    def get_attribute(data, attr):
        if(data.find_next("div", string=attr)): 
            return data.find_next("div", string=attr).parent.find_next(class_='uk-width-1-2 uk-text-bold').text.strip('\n\t ')
        else:
            return ''
    
    @staticmethod
    def get_car(url):
        resp = requests.get(url, headers={'User-Agent': 'MyScraper'})
        resp.raise_for_status()
        car_page = BeautifulSoup(resp.text, 'html.parser')

        data = car_page.find_all(class_='infoBox')[0]
        data1 = car_page.find_all(class_='infoBox')[1]
            
        try:
            car = {
                'ID': url.split('/')[4],
                'URL': url,
                'price': car_page.find_all(class_='priceClassified')[0].text[:-2],
                'brand': CarScrapper.get_attribute(data, 'Marka'),
                'model': CarScrapper.get_attribute(data, 'Model'),
                'year': CarScrapper.get_attribute(data, 'Godište'),
                'mileage': CarScrapper.get_attribute(data, 'Kilometraža')[:-4],
                'bodywork': CarScrapper.get_attribute(data, 'Karoserija'),
                'fuel': CarScrapper.get_attribute(data, 'Gorivo'),
                'volume': CarScrapper.get_attribute(data, 'Kubikaža'),
                'power': CarScrapper.get_attribute(data, 'Snaga motora').split('/')[0],
                'fixed_price': CarScrapper.get_attribute(data, 'Fiksna cena'),
                'date_posted': CarScrapper.get_attribute(data, 'Datum postavke:'),

                'DMFW': CarScrapper.get_attribute(data1, 'Plivajući zamajac'),
                'emission': CarScrapper.get_attribute(data1, 'Emisiona klasa motora'),
                'transmission': CarScrapper.get_attribute(data1, 'Menjač'),
                'door': CarScrapper.get_attribute(data1, 'Broj vrata'),
                'seats': CarScrapper.get_attribute(data1, 'Broj sedišta'),
                'color': CarScrapper.get_attribute(data1, 'Boja'),
                'registered': CarScrapper.get_attribute(data1, 'Registrovan do'),
                'origin': CarScrapper.get_attribute(data1, 'Poreklo vozila'),
                'country_origin': CarScrapper.get_attribute(data1, 'Zemlja uvoza')
            }   
            
            car['price'] = car['price'].replace('.', '')
            car['mileage'] = car['mileage'].replace('.', '')

            # Fixing some semantic errors
            if(car['date_posted']==''): car['date_posted'] = CarScrapper.get_attribute(data, 'Datum obnove:')



            return car
            
        except Exception as error:
            # handle the exception
            print(f'{datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")} - An exception occurred: {error}')
            car = {}
            return car




base_url = 'https://www.polovniautomobili.com/auto-oglasi/pretraga?page='
cars = []
filter = '&sort=renewDate_desc&city_distance=0&showOldNew=all&without_price=1'

print(datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S"))
log = []

for page in range(1,400):
    url = f'{base_url}{page}{filter}'

    response = requests.get(url, headers={'User-Agent': 'MyScraper'})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    listings = soup.select('.ordinaryClassified')  # Multiple possible selectors

    i = 1

    for listing in listings:
        link = 'https://www.polovniautomobili.com' + listing.find_all('a', href=True)[0]['href']
        car = CarScrapper.get_car(link)
        cars.append(car)
            
        
        print(f'{page} - {i}')
        i+=1
        #time.sleep(random.randint(0, 2)) 


df = pd.DataFrame(cars)
df.to_csv(f'car_data_{datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")}.csv', index=False, encoding='utf-8')

with open(f'log_{datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")}.csv', "a") as f:
  f.write('\n'.join(log))