import asyncio
import aiohttp
import datetime
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

# Helper function
def get_attribute(data, attr):
    tag = data.find_next("div", string=attr)
    if tag:
        return tag.parent.find_next(class_='uk-width-1-2 uk-text-bold').text.strip('\n\t ')
    return ''

# Async car scraper
async def get_car(session, url, sem):
    async with sem:  # limit concurrency
        try:
            async with session.get(url, headers={'User-Agent': 'MyScraper'}) as resp:
                html = await resp.text()
                car_page = BeautifulSoup(html, 'lxml')  # lxml is faster

                data = car_page.find_all(class_='infoBox')[0]
                data1 = car_page.find_all(class_='infoBox')[1]

                car = {
                    'ID': url.split('/')[4],
                    'URL': url,
                    'price': car_page.find_all(class_='priceClassified')[0].text[:-2].replace('.', ''),
                    'brand': get_attribute(data, 'Marka'),
                    'model': get_attribute(data, 'Model'),
                    'year': get_attribute(data, 'Godište'),
                    'mileage': get_attribute(data, 'Kilometraža')[:-4].replace('.', ''),
                    'bodywork': get_attribute(data, 'Karoserija'),
                    'fuel': get_attribute(data, 'Gorivo'),
                    'volume': get_attribute(data, 'Kubikaža'),
                    'power': get_attribute(data, 'Snaga motora').split('/')[0],
                    'fixed_price': get_attribute(data, 'Fiksna cena'),
                    'date_posted': get_attribute(data, 'Datum postavke:') or get_attribute(data, 'Datum obnove:'),

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

                return car

        except Exception as error:
            print(f'{datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")} - Error: {error}')
            return {}

# API endpoint
@app.route('/get_page/<page_number>', methods=['GET'])
async def get_page(page_number):
    base_url = 'https://www.polovniautomobili.com/auto-oglasi/pretraga?page='
    filter = '&sort=renewDate_desc&city_distance=0&showOldNew=all&without_price=1'

    url = f'{base_url}{page_number}{filter}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'User-Agent': 'MyScraper'}) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'lxml')

            listings = soup.select('.ordinaryClassified')
            links = ['https://www.polovniautomobili.com' + l.find('a', href=True)['href'] for l in listings]

            # semaphore to limit concurrency (e.g., 10 at a time)
            sem = asyncio.Semaphore(10)

            tasks = [get_car(session, link, sem) for link in links]
            cars = await asyncio.gather(*tasks)
            return jsonify(cars)

if __name__ == '__main__':
    app.run(debug=True)
