import sys
import getopt
import urllib.request
import re
import googlemaps
import pymongo
import logging
import pprint

from bs4 import BeautifulSoup
from pymongo import MongoClient


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
    return MongoClient().koala_tanken


def insert_record(record):
    try:
        db.stations.insert_one(record)
    except Exception as insert_ex:
        logger.error('could not insert record. please add manually')
        logger.error(insert_ex)
        insert_error_record(record)


def insert_error_record(record):
    try:
        db.error_stations.insert_one(record)
    except Exception as error_ex:
        logger.error('could not insert error record: {}'.format(record))
        logger.error(error_ex)


def find_record(record):
    return db.stations.find_one(record)


def find_all_records(record):
    return db.stations.find(record)


def remove_all():
    db.stations.delete_many({})


def create_index():
    try:
        db.stations.create_index([('loc', pymongo.GEOSPHERE)])
    except Exception as ex:
        logger.error(ex)


def print_db_contents():
    print('printing stations table:')
    for record in db.stations.find():
        logger.debug(pprint.pformat(record))


def miles_to_radian(miles):
    earth_radius_in_miles = 3959
    return miles / earth_radius_in_miles


'''
> Main procedure code
'''
# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# add where the information must be logged to
fileLogHandler = logging.FileHandler('logfile.log')
stdStreamHandler = logging.StreamHandler()
# log format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fileLogHandler.setFormatter(formatter)
stdStreamHandler.setFormatter(formatter)
# add handlers
logger.addHandler(fileLogHandler)
logger.addHandler(stdStreamHandler)

logger.info('starting koala_tanken tool...')

# starting url for retrieving the fuel stations and info
BASE_URL = 'http://www.brandstof-zoeker.nl'

# initializes db
db = initialize_db()

# starting index of scraping tool
startIndex = 0
apiKey = 'AIzaSyBoqTuFSXre_0F0j9IGHtAiqRfP6VwaxE8'
# apiKey = 'AIzaSyCyarQ-B7tOnY4hhrQYXrO3_TH3wHidcE4' # new api key
# apiKey = 'AIzaSyBa74BR6m5XwupzKTaq5FVY8QJXIIhRtrQ'
# apiKey = 'AIzaSyCR883xLQrbS98hEshOePFIlrc9vaf9Cr4'

# option -r to clear database. usage: app.py -r
# option -i to indicate starting index. usage: app.py -i 2345
# option -g to specify a google maps api key. usage: app.py -g bIGass4p1k3yg03sh3r3
options, args = getopt.getopt(sys.argv[1:], 'ri:g:')
for option, arg in options:
    logger.info('found option {} with arg {}'.format(option, arg))
    if option == '-r':
        remove_all()
    elif option == '-i':
        startIndex = int(arg)
    elif option == '-g':
        apiKey = arg

logger.info('starting at index: {}'.format(startIndex))
logger.info('google api key: {}'.format(apiKey))

# initializes the google maps api
gmaps = googlemaps.Client(key=apiKey)

# with open('content/data/fuel_1.json') as data_file:
#     data = json.load(data_file)
#     location = gmaps.geocode(data['addressLine'] + ', ' + data['postalCode'])[0]['geometry']['location']
#     coords = [location['lng'], location['lat']]
#     data['loc'] = {
#         'type': 'Point',
#         'coordinates': [4.342460, 52.080592]
#     }
#     insert_record(data)
#
# with open('content/data/fuel_2.json') as data_file:
#     data = json.load(data_file)
#     location = gmaps.geocode(data['addressLine'] + ', ' + data['postalCode'])[0]['geometry']['location']
#     coords = [location['lng'], location['lat']]
#     data['loc'] = {
#         'type': 'Point',
#         'coordinates': [4.344777, 52.079062]
#     }
#     insert_record(data)
#
# with open('content/data/fuel_3.json') as data_file:
#     data = json.load(data_file)
#     location = gmaps.geocode(data['addressLine'] + ', ' + data['postalCode'])[0]['geometry']['location']
#     coords = [location['lng'], location['lat']]
#     data['loc'] = {
#         'type': 'Point',
#         'coordinates': [4.339944, 52.076493]
#     }
#     insert_record(data)


# print_db_contents()
# create_index()

'''
> Example on how to search for stations within a certain radius.
'''
# records = db.stations.find({
#     'loc': {
#         '$geoWithin': {
#             '$centerSphere': [[4.339034, 52.079738], miles_to_radian(5)]
#         }
#     }
# })
# pprint(records)
#
# for record in records:
#     pprint(record)
# for detail in find_all_records({'fuelDetails.moreOrLess': {'$gt' : 0}}):
#     pprint(detail)
'''
< Example ...
'''


# ensures that the url doesn't end in '/ or ’/ as these url's go back to the main page
pattern = re.compile('(?!.*\'/$)(?!.*’/$)(?!.*0/$)')
postal_pattern = re.compile('^\d{4}')

mainPage = retrieve_soup(BASE_URL + '/station/')
letterListDiv = mainPage.find_all('div', attrs={'class': 'left'})

# get links from the main/index page
links = []
for div in letterListDiv:
    anchors = div.findAll('a')
    for a in anchors:
        href = a['href']
        if pattern.match(href):
            links.append(a['href'])

# get all the links to the station details page
stationLinks = []
for link in links:
    stationListPage = retrieve_soup(BASE_URL + link)
    stationListDiv = stationListPage.findAll('div', attrs={'class': 'left'})
    for div in stationListDiv:
        anchors = div.findAll('a')
        for a in anchors:
            href = a['href']
            if '/station' in href:
                stationLinks.append(href)


# scrape details of ALL stations
logger.info('processing {} stations...'.format(len(stationLinks)))
logger.info('==========================================================================')
stationIndex = startIndex
for stationLink in stationLinks[startIndex:]:
    fullUrl = BASE_URL + stationLink
    logger.info('processing station index # {} at url {}'.format(stationIndex, fullUrl))
    stationIndex += 1

    stationSoup = retrieve_soup(fullUrl)

    # get DOM of the details div
    stationDetailsDivs = stationSoup.findAll('div', attrs={'class': 'left'})
    for div in stationDetailsDivs:
        # get fuel station address details
        half1Div = div.findAll('div', attrs={'class': 'half1'})
        addressContents = half1Div[0].contents
        name = addressContents[2].strip(' \t\n\r')
        addressLine = addressContents[4].strip(' \t\n\r')
        anchors = half1Div[0].findAll('a')

        postalCode = anchors[0].getText() + ' ' + anchors[1].getText()
        if not postal_pattern.match(anchors[0].getText()):
            logger.info('postal code does not match pattern. getting from addressContents[6]')
            postalCode = addressContents[6].strip(' \t\n\r') + ' ' + anchors[0].getText()

        logger.debug('addressContents: {}'.format(addressContents))
        logger.debug('name: {}'.format(name))
        logger.debug('addressLine: {}'.format(addressLine))
        logger.debug('anchors: {}'.format(anchors))

        location = {}
        coords = []
        try:
            location = gmaps.geocode(addressLine + ', ' + postalCode)[0]['geometry']['location']
            logger.info('found the following location: lat:{}, lng:{}'.format(location['lat'], location['lng']))
            coords.append(location['lng'])
            coords.append(location['lat'])
        except Exception as e:
            logger.error('did not find location for address due to exception:')
            logger.error(e)

        fuelStation = {
            'name': name,
            'addressLine': addressLine,
            'postalCode': postalCode,
            'loc': {
                'type': 'Point',
                'coordinates': coords
            },
            'fuelDetails': []
        }

        # getting the fuel details
        half2Div = div.findAll('div', attrs={'class': 'half2'})
        if len(half2Div) == 0:
            logger.warning('FUEL DETAILS WERE NOT FOUND FOR THIS STATION!')
            logger.warning('inserting fuel station details:')
            logger.warning(pprint.pformat(fuelStation))
            insert_record(fuelStation)
            continue

        fuelTypeTags = half2Div[0].findAll('dt')
        fuelPriceTags = half2Div[0].findAll('dd')
        for index, fuelTypeTag in enumerate(fuelTypeTags):
            # get the fuel type
            fuelType = fuelTypeTag.getText().strip()
            # get the prices and more-or-less status of the first fuel type
            fuelPriceStr = fuelPriceTags[index].getText()
            prices = re.findall(r'\d+\.*\d*', fuelPriceStr)
            fuelPrice = float(prices[0])
            moreOrLessPrice = float(prices[len(prices) - 1])
            isLess = 'goedkoper' in fuelPriceStr
            moreOrLessPrice = moreOrLessPrice * -1 if isLess else moreOrLessPrice
            # add fuel price details to fuelStation object
            fuelStation['fuelDetails'].append({
                'fuelType': fuelType,
                'price': fuelPrice,
                'moreOrLess': moreOrLessPrice
            })

        logger.info('inserting fuel station details:')
        logger.info(pprint.pformat(fuelStation))
        insert_record(fuelStation)

    logger.info('==========================================================================')

create_index()
