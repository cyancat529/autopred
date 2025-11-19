import requests
from bs4 import BeautifulSoup
import pandas as pd

###         polovniautomobili.com scraper
###   VERSION 1 - Direct scraping from index pages

base_url = 'https://www.polovniautomobili.com/auto-oglasi/pretraga?page='
cars = []

for page in range(1,11):
    url = f'{base_url}{page}'

    response = requests.get(url, headers={'User-Agent': 'MyScraper'})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    listings = soup.select('.ordinaryClassified')  # Multiple possible selectors

    i = 1

    for listing in listings:
        try:
            car = {
                'title': listing.find_all(class_= 'ga-title')[0].string.strip('\n\t'),
                'price': listing.find_all(class_= 'price')[0].span.string.strip('\n\t')[:-2],
                'year': listing.find_all(class_='setInfo')[0].div.string[:4],
                'type': listing.find_all(class_='setInfo')[0].div.string[6:],
                'fuel': listing.find_all(class_='bottom')[0].text.split(" | ")[0],
                'volume': listing.find_all(class_='bottom')[0].text.split(" | ")[1].split(' ')[0],
                'mileage': listing.find_all(class_='top')[1].text[:-3],
                'location': listing.find_all(class_='city')[0].text[1:]
            }
            car['price'] = car['price'].replace('.', '')
            car['mileage'] = car['mileage'].replace('.', '')
            cars.append(car)
        except:
            car = {}

        


df = pd.DataFrame(cars)
df.to_csv('car_data.csv', index=False, encoding='utf-8')

