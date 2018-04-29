from connectionHelper.Collection import getCollection, getDb


class TripStore:

    __db = None
    __connection = None
    __valid_trips = None

    def __init__(self):
        self.__db, self.__connection = getDb()
        self.__valid_trips = getCollection(self.__db, 'valid_trips')
        # print(self.__valid_trips)

    def getTrips(self, startDateTime, endDateTime):
        result = self.__valid_trips.find({
            'tpep_pickup_datetime': {
                '$gte': self.__formatDate(startDateTime),
                '$lt': self.__formatDate(endDateTime)
            }
        })

        return list(result)

    def getAverageTripMetrics(self, pickupCoordinates, dropoffCoordinates):
        result = self.__valid_trips.aggregate([{
            '$match': {
                '$and': [{
                    'pickup_location': {
                        '$geoWithin': {'$centerSphere': [pickupCoordinates, 2 / 6378.1]}
                    }
                }, {
                    'dropoff_location': {
                        '$geoWithin': {'$centerSphere': [dropoffCoordinates, 2 / 6378.1]}
                    }
                }]
            }
        }, {'$limit': 50}, {'$group': {
            '_id': 'null',
            'avgDistance': {'$avg': '$trip_distance'}
        }}])

        result = list(result)
        return result[0]

    def disposeConnection(self):
        self.__connection.close()

    def __formatDate(self, dateTime):
        return str(dateTime)