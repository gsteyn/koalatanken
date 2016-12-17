import urllib.request
import re
from bs4 import BeautifulSoup

import pymongo
import datetime
import pprint

'''
Functions for managing common tasks for getting and processing dom.
'''


# Retrieves a soup(html dom) from the given url.
def retrieve_soup(url, parser='html.parser'):
    # print('retrieving soup from -> ' + url)
    request = urllib.request.urlopen(url)
    soup = BeautifulSoup(request.read(), parser)
    return soup

'''
DB related functions
'''

def initialize_db():
    from pymongo import MongoClient
    client = MongoClient()
    return client.test_database

def insert_record(record):
    db.stations.insert_one(record)

def find_record(record):
    return db.stations.find_one(record)

def remove_all():
    db.stations.delete_many({})

'''
> Main procedure code
'''
# starting url for retrieving the fuel stations and info
BASE_URL = 'http://www.brandstof-zoeker.nl/'

# initializes db
db = initialize_db()
remove_all()

# ensures that the url doesn't end in '/ or ’/ as these url's go back to the main page
pattern = re.compile('(?!.*\'/$)(?!.*’/$)(?!.*0/$)')

mainPage = retrieve_soup(BASE_URL + 'station/')
letterListDiv = mainPage.find_all('div', attrs={'class': 'left'})

links = []
for div in letterListDiv:
    anchors = div.findAll('a')
    for a in anchors:
        href = a['href']
        if pattern.match(href):
            links.append(a['href'])

stationLinks = []
for link in links:
    stationListPage = retrieve_soup(BASE_URL + link)
    stationListDiv = stationListPage.find_all('div', attrs={'class': 'left'})
    for div in stationListDiv:
        anchors = div.findAll('a')
        for a in anchors:
            href = a['href']
            if '/station' in href:
                stationLinks.append(href)

print(stationLinks)


for station in stationLinks:
    json_station = {'station': station}
    insert_record(json_station)

for post in find_record({'station': '/station/total-sss-de-stoven-zutphen-2037/'}):
    print(post)


