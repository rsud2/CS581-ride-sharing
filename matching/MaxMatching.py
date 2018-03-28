import copy

from stores.RouteStore import RouteStore

MAX_PASSENGER_COUNT = 4

def getPassengerCount(tripsSet):
    passengers = 0
    for trip in tripsSet:
        passengers += trip['passenger_count']

    return passengers

def calculateScore(tripSet1, stripSet2):
    # TODO :
    originalDistance = 0
    combinedList = tripSet1 + stripSet2
    for trip in combinedList:
        originalDistance += trip['trip_distance']

    routedDistance = RouteStore().getRouteInfo()

    return 0

def mergeSets(list1, list2):
    return list1 + list2


def maxMatching(trips, distanceMatrix):

    __trips = copy.deepcopy(trips)

    currentMerges = []
    for trip in __trips:
        currentMerges.append({'trips': [trip]})

    mergeScores = {}

    # init
    for i in range(len(currentMerges)):
        for j in range(i):
            mergeScores[i, j] = 0

    # invalidate based on passenger count
    for i in range(len(currentMerges)):
        for j in range(i):
            passengers = getPassengerCount(currentMerges[i]['trips']) + getPassengerCount(currentMerges[j]['trips'])
            if passengers > MAX_PASSENGER_COUNT:
                mergeScores[i, j] = float('-inf')

    # update scores
    for i in range(len(currentMerges)):
        for j in range(i):

            # skip invalidated combinations
            if mergeScores[i, j] == float('-inf'):
                continue

            # asdf
            mergeScores[i, j] = calculateScore(currentMerges[i]['trips'], currentMerges[j]['trips'])

    # pick maximums to get next level of merges
    weightedList = []
    for i in range(len(currentMerges)):
        for j in range(i):
            weightedList.append({ 'i' : i, 'j': j, 'weight': mergeScores[i, j] })

    newMerges = []

    while len(weightedList) > 0:
        weightedList = sorted(weightedList, key=lambda k: k['weight'])
        maxWeightItem = weightedList[-1]

        # remove all items from weightedList where i or j have same values as in maxWeightItem
        tmpList = []
        for item in weightedList:
            if item['i'] != maxWeightItem['i'] and item['j'] != maxWeightItem['j']:
                tmpList.append(item)

        weightedList = tmpList

        newMerges.append({'trips': mergeSets(currentMerges[maxWeightItem['i']]['trips'], currentMerges[maxWeightItem['j']]['trips'])})


