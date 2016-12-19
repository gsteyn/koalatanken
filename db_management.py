import logging
from pymongo import MongoClient
from bson.objectid import ObjectId


def initialize_db():
    return MongoClient().koala_tanken
    # return MongoClient().test_database


def count_stations():
    return len(list(db.stations.find()))


def count_error_stations():
    return len(list(db.error_stations.find()))


def find_all():
    return list(db.stations.find())


def find_record(record):
    return db.stations.find_one(record)


def find_stations_duplicate():
    duplicates = db.stations.aggregate([
        {'$group': {
            '_id': {'name': '$name'},
            'uniqueIds': {'$addToSet': '$_id'},
            'count': {'$sum': 1}
        }},
        {'$match': {
            'count': {'$gte': 2}
        }},
        {'$sort': {'count': -1}},
        {'$limit': 10000}
    ])
    return list(duplicates)


def remove_record(duplicate_id):
    return db.stations.delete_one({'_id': ObjectId(duplicate_id)})


db = initialize_db()

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# add where the information must be logged to
fileLogHandler = logging.FileHandler('logfile_duplicates.log')
stdStreamHandler = logging.StreamHandler()
# log format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fileLogHandler.setFormatter(formatter)
stdStreamHandler.setFormatter(formatter)
# add handlers
logger.addHandler(fileLogHandler)
logger.addHandler(stdStreamHandler)

logger.info('starting koala_tanken duplicate records tool...')

logger.info('stations: {}'.format(count_stations()))
logger.info('error_stations: {}'.format(count_error_stations()))

logger.info('--------------------------------------------------------------------------')
dups = find_stations_duplicate()
for duplicate in dups:
    logger.info('duplicates found for \'{}\': {}'.format(duplicate['_id']['name'], duplicate['count']))
    uniqueIds = duplicate['uniqueIds']
    logger.info('keeping record with id: \'{}\''.format(uniqueIds[0]))
    for stationId in uniqueIds[1:]:
        logger.info('removing id: {}'.format(stationId))
        result = remove_record(stationId)
        logger.info('records deleted: {}'.format(result.deleted_count))
    logger.info('--------------------------------------------------------------------------')

logger.info('after cleanup -> stations: {}'.format(count_stations()))
logger.info('error_stations: {}'.format(count_error_stations()))
logger.info('after cleanup -> duplicates: {}'.format(find_stations_duplicate()))
logger.info('==========================================================================')

# result = db.stations.delete_one({'_id': ObjectId('5855830b36fe6842743621f4')})
# print(result.deleted_count)
#
# for rec in find_all():
#     print(rec)
#
# record = find_record({'name': 'LUKOIL Express - WIJK EN AALBURG'})
# print(record)
