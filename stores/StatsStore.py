from connectionHelper.Collection import getDb, getCollection


class StatsStore:
    __db = None
    __connection = None
    __stats = None

    def __init__(self):
        self.__db, self.__connection = getDb()
        self.__stats = getCollection(self.__db, 'stats')
        # print(self.__valid_trips)

    def save(self, stats):
        self.__stats.insert_one(stats)
