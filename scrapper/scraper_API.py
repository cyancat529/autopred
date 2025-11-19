import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

###       polovniautomobili.com scraper
###        VERSION 4 - API scrapping

# Internal functions

def get_attribute(data, attr):
    if(data.find_next("div", string=attr)): 
        return data.find_next("div", string=attr).parent.find_next(class_='uk-width-1-2 uk-text-bold').text.strip('\n\t ')
    else:
        return ''


async def get_car(session, url):
    async with session.get(url) as resp:
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
                'brand': get_attribute(data, 'Marka'),
                'model': get_attribute(data, 'Model'),
                'year': get_attribute(data, 'Godište'),
                'mileage': get_attribute(data, 'Kilometraža')[:-4],
                'bodywork': get_attribute(data, 'Karoserija'),
                'fuel': get_attribute(data, 'Gorivo'),
                'volume': get_attribute(data, 'Kubikaža'),
                'power': get_attribute(data, 'Snaga motora').split('/')[0],
                'fixed_price': get_attribute(data, 'Fiksna cena'),
                'date_posted': get_attribute(data, 'Datum postavke:'),

                'DMFW': get_attribute(data1, 'Plivajući zamajac'),
                'emission': get_attribute(data1, 'Emisiona klasa motora'),
                'transmission': get_attribute(data1, 'Menjač'),
                'door': get_attribute(data1, 'Broj vrata'),
                'seats': get_attribute(data1, 'Broj sedišta'),
                'color': get_attribute(data1, 'Boja'),
                'registered': get_attribute(data1, 'Registrovan do'),
                'origin': get_attribute(data1, 'Poreklo vozila'),
                'country_origin': get_attribute(data1, 'Zemlja uvoza')
            }   
            
            car['price'] = car['price'].replace('.', '')
            car['mileage'] = car['mileage'].replace('.', '')

            # Fixing some semantic errors
            if(car['date_posted']==''): car['date_posted'] = get_attribute(data, 'Datum obnove:')


            
        except Exception as error:
            # handle the exception
            print(f'{datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")} - An exception occurred: {error}')
            car = {}
        
        return car


# API functions

@app.route('/get_page/<page_number>', methods=['GET'])
async def get_page(page_number):
    base_url = 'https://www.polovniautomobili.com/auto-oglasi/pretraga?page='
    filter = '&year_to=2000&sort=renewDate_desc&city_distance=0&showOldNew=all&without_price=1'

    url = f'{base_url}{page_number}{filter}'

    response = requests.get(url, headers={'User-Agent': 'MyScraper'})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    listings = soup.select('.ordinaryClassified')  # Multiple possible selectors

    cars = []

    links = []

    for listing in listings:
        links.append('https://www.polovniautomobili.com' + listing.find_all('a', href=True)[0]['href'])
        
    async with aiohttp.ClientSession() as session:
        tasks = [get_car(session, link) for link in links]
        cars = await asyncio.gather(*tasks)
        return jsonify(cars)

if __name__ == '__main__':
   app.run(debug=True)