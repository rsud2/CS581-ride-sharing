from pymongo import MongoClient


def getDb():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.get_database('trip_info')

    return (db, client)

def getCollection(db, collectionName):
    return db.get_collection(collectionName)