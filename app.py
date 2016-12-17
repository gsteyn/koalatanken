import urllib.request
import re
from pprint import pprint
import json

from bs4 import BeautifulSoup
from pymongo import MongoClient
import googlemaps


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
    return MongoClient().test_database

def insert_record(record):
    db.stations.insert_one(record)

def find_record(record):
    return db.stations.find_one(record)

def find_all_records(record):
    return db.stations.find(record)

def remove_all():
    db.stations.delete_many({})

def print_db_contents():
    for record in db.stations.find():
        pprint(record)

'''
> Main procedure code
'''
# starting url for retrieving the fuel stations and info
BASE_URL = 'http://www.brandstof-zoeker.nl/'

# initializes db
db = initialize_db()
remove_all()

# initializes the google maps api
gmaps = googlemaps.Client(key='AIzaSyCR883xLQrbS98hEshOePFIlrc9vaf9Cr4')

with open('content/data/fuel_1.json') as data_file:
    data = json.load(data_file)
    data['location'] = gmaps.geocode(data['addressLine2'] + ', ' + data['postalCode'])[0]['geometry']['location']
    insert_record(data)

with open('content/data/fuel_2.json') as data_file:
    data = json.load(data_file)
    data['location'] = gmaps.geocode(data['addressLine2'] + ', ' + data['postalCode'])[0]['geometry']['location']
    insert_record(data)

with open('content/data/fuel_3.json') as data_file:
    data = json.load(data_file)
    data['location'] = gmaps.geocode(data['addressLine2'] + ', ' + data['postalCode'])[0]['geometry']['location']
    insert_record(data)

# for detail in find_all_records({'fuelDetails.moreOrLess': {'$gt' : 0}}):
#     pprint(detail)

print_db_contents()

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


