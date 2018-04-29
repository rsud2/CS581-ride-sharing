import copy
import pprint

from config import RideSharingConfig
from helpers.statistics import getStatistics
from stores.RouteStore import RouteStore

# MAX_PASSENGER_COUNT = 5
# MAX_MERGED_TRIPS = 5


def getPassengerCount(tripsSet):
    passengers = 0
    for trip in tripsSet:
        passengers += trip['passenger_count']

    return passengers


def calculateScore(tripSet1, stripSet2):
    originalDistance = 0
    combinedList = tripSet1 + stripSet2
    for trip in combinedList:
        originalDistance += trip['trip_distance']

    # TODO : picking the pickup point of first trip at random. see if wee can fix this
    tripStartLocation = combinedList[0]['pickup_location']['coordinates']
    waypoints = []
    waypoints.append(combinedList[0]['dropoff_location']['coordinates'])

    for i in range(1, len(combinedList)):
        waypoints.append(combinedList[i]['dropoff_location']['coordinates'])

    routingInfo = RouteStore().getRouteInfo2(tripStartLocation, waypoints)

    return originalDistance - routingInfo['distance']


def mergeSets(list1, list2):
    return list1 + list2

# Actual public method. Others are just helpers
def maxMatching(heuristicMatchedSets):

    # __trips = copy.deepcopy(trips)
    #
    # currentMerges = []
    # for trip in __trips:
    #     currentMerges.append({'trips': [trip]})

    currentMerges = heuristicMatchedSets

    for tripMergeCounter in range(RideSharingConfig.MAX_MERGED_TRIPS):

        mergeScores = {}

        # init
        for i in range(len(currentMerges)):
            for j in range(i):
                mergeScores[i, j] = 0

        # invalidate based on passenger count
        for i in range(len(currentMerges)):
            for j in range(i):
                passengers = getPassengerCount(currentMerges[i]['trips']) + getPassengerCount(currentMerges[j]['trips'])
                if passengers > RideSharingConfig.MAX_PASSENGER_COUNT:
                    mergeScores[i, j] = float('-inf')

        # update scores  ## TODO : parallelize this nested loop
        for i in range(len(currentMerges)):
            for j in range(i):

                # skip invalidated combinations
                if mergeScores[i, j] == float('-inf'):
                    continue

                mergeScores[i, j] = calculateScore(currentMerges[i]['trips'], currentMerges[j]['trips'])

        # pick maximums to get next level of merges
        weightedList = []
        for i in range(len(currentMerges)):
            for j in range(i):
                weightedList.append({ 'i' : i, 'j': j, 'weight': mergeScores[i, j] })

        newMerges = []
        copiedIdxSet = {}
        while len(weightedList) > 0:
            weightedList = sorted(weightedList, key=lambda k: k['weight'])
            maxWeightItem = weightedList[-1]

            # no more matchings with a positive score; don't try to merge
            if maxWeightItem['weight'] <= 0:
                # TODO : all remaining items in weightedList need to be carried forward to 'newMerges' as-is
                remainingIdxSet = {}
                for item in weightedList:
                    i = item['i']
                    j = item['j']

                    remainingIdxSet[i] = True
                    remainingIdxSet[j] = True

                for key in list(remainingIdxSet.keys()):

                    if key not in list(copiedIdxSet.keys()):
                        newMerges.append(currentMerges[key])

                break

            # remove all items from weightedList where i or j have same values as in maxWeightItem
            i = maxWeightItem['i']
            j = maxWeightItem['j']

            copiedIdxSet[i] = True
            copiedIdxSet[j] = True

            tmpList = []
            for item in weightedList:
                if item['i'] != i and item['j'] != j:
                    tmpList.append(item)

            weightedList = tmpList
            newMerges.append({'trips': mergeSets(currentMerges[i]['trips'], currentMerges[j]['trips']),
                              'distanceGain': maxWeightItem['weight']})

        currentMerges = newMerges

        stats = getStatistics(currentMerges)
        print("Max Matching - iter {0} :: Original : {1}, Merged : {2}".format(tripMergeCounter + 1, stats['totalOriginalDistance'], stats['totalMergedDistance']))


    # pprint.pprint(newMerges)

    return newMerges
