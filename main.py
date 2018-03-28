import datetime

import itertools
from time import sleep

from bson import ObjectId
from matplotlib.axes._base import _process_plot_var_args
from multiprocessing import Process
from pymongo import MongoClient

from timeit import default_timer as timer
from joblib import Parallel, delayed

import pprint

from helpers.distance import points2distance, decdeg2dms


def getAvgStats(tripStore, trip):
    result = tripStore.getAverageTripMetrics(trip['pickup_location']['coordinates'],
                                             trip['dropoff_location']['coordinates'])
    result['_id'] = trip['_id']

    return result


def getAllAvgStats(tripStore, trips):
    averageStatsList = Parallel(n_jobs=-1, backend="threading")(
        delayed(getAvgStats)(store, trip) for store in itertools.repeat(tripStore, len(trips)) for trip in trips)

    return averageStatsList


def getRouteInfo(trip):
    result = RouteStore().getRouteInfo(trip['pickup_location']['coordinates'],
                                       [ trip['dropoff_location']['coordinates'] ])
    result['_id'] = trip['_id']
    return result


def getAllRouteInfo(trips):
    routeInfoList = Parallel(n_jobs=4, backend="threading")(
        delayed(getRouteInfo)(trip) for trip in trips)

    return routeInfoList


# def getPairWiseDistance(tripsTuple):
#     trip1, trip2 = tripsTuple
#     result = RouteStore().getRouteInfo(trip1['dropoff_location']['coordinates'],
#                                        trip2['dropoff_location']['coordinates'])
#
#     return {'t1': trip1['_id'], 't2': trip2['_id'], 'result': result}
#
#
# def getAllPairwiseDistances(trips):
#     distanceMatrix = []
#     pairwiseList = []
#     for i in range(len(trips)):
#         for j in range(i):
#             pairwiseList.append((trips[i], trips[j]))
#
#     results = Parallel(n_jobs=4, backend="threading")(
#         delayed(getPairWiseDistance)(pair) for pair in pairwiseList)
#
#     for result in results:
#         i = -1
#         j = -1
#         for idx, trip in enumerate(trips):
#             if result['t1'] == trip['_id']:
#                 i = idx  # this is erroneous
#
#             if result['t2'] == trip['_id']:
#                 j = idx  # this is erroneous
#
#         distanceMatrix[i, j] = result['result']
#
#     return distanceMatrix

def getAllPairwiseDistances2(trips):
    distanceMatrix = {}
    for i in range(len(trips)):
        for j in range(i):
            t1Long = decdeg2dms(trips[i]['dropoff_location']['coordinates'][0])
            t1Lat = decdeg2dms(trips[i]['dropoff_location']['coordinates'][1])

            t2Long = decdeg2dms(trips[j]['dropoff_location']['coordinates'][0])
            t2Lat = decdeg2dms(trips[j]['dropoff_location']['coordinates'][1])

            val = points2distance([t1Long, t1Lat], [t2Long, t2Lat])
            distanceMatrix[i, j] = val

    return distanceMatrix


# define main
if __name__ == '__main__':
    from stores.TripStore import TripStore
    from stores.RouteStore import RouteStore

    MAX_PASSENGER_COUNT = 4

    tripStore = TripStore()

    startDateTime = datetime.datetime(2016, 1, 1, 14, 10, 0)
    endDateTime = startDateTime + datetime.timedelta(seconds=5 * 60)  # trip merge window of 5 minutes

    for i in range(10):

        start = timer()

        if i != 0:
            startDateTime = endDateTime

        endDateTime = startDateTime + datetime.timedelta(seconds=5 * 60)  # trip merge window of 5 minutes

        trips = tripStore.getTrips(startDateTime, endDateTime)

        routeInfoList = getAllRouteInfo(trips)
        avgStatList = getAllAvgStats(TripStore(), trips)
        distanceMatrix = getAllPairwiseDistances2(trips)

        end = timer()

        # no. of infeasible combinations
        feasibleL1Merges = {}
        for i in range(len(trips)):
            for j in range(i):
                feasibleL1Merges[i, j] = True

        for i in range(len(trips)):
            for j in range(i):
                if distanceMatrix[i, j] > trips[i]['trip_distance'] and distanceMatrix[i, j] > trips[j]['trip_distance']:
                    feasibleL1Merges[i, j] = False
                if trips[i]['passenger_count'] + trips[j]['passenger_count'] > MAX_PASSENGER_COUNT:
                    feasibleL1Merges[i, j] = False

        infeasibleL1Combinations = 0
        # just counting; nothing insidious
        for i in range(len(trips)):
            for j in range(i):
                if not feasibleL1Merges[i, j]:
                    infeasibleL1Combinations += 1

        print('Runtime Stats  : Iteration {0}, Trip Requests {1}, Time Taken {2}s, StartTime {3}, Infeasible L1 Combinations {4}, Feasible L1 Combinations {5}'
              .format(i, len(trips), end - start, str(startDateTime), infeasibleL1Combinations, ((pow(len(trips), 2) - len(trips)) / 2) - infeasibleL1Combinations))
