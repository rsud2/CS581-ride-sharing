from config import RideSharingConfig
from stores.RouteStore import RouteStore

# EUCLIDEAN_DISTANCE_DIFF_MULTIPLIER = 1
# MAX_PASSENGER_COUNT = 4

def heutisticMatch(trips, distanceMatrix):
    # no. of infeasible combinations
    feasibleL1Merges = {}
    for i in range(len(trips)):
        for j in range(i):
            feasibleL1Merges[i, j] = True

    for i in range(len(trips)):
        for j in range(i):
            if (RideSharingConfig.EUCLIDEAN_DISTANCE_DIFF_MULTIPLIER * distanceMatrix[i, j]) > trips[i]['trip_distance'] \
                    and (RideSharingConfig.EUCLIDEAN_DISTANCE_DIFF_MULTIPLIER * distanceMatrix[i, j]) > trips[j]['trip_distance']:

                feasibleL1Merges[i, j] = False
            elif trips[i]['passenger_count'] + trips[j]['passenger_count'] > RideSharingConfig.MAX_PASSENGER_COUNT:
                feasibleL1Merges[i, j] = False
            else:
                opt1 = abs(distanceMatrix[i, j] - trips[i]['trip_distance'])
                opt2 = abs(distanceMatrix[i, j] - trips[j]['trip_distance'])
                feasibleL1Merges[i, j] = max(opt1, opt2)

    # cleanup
    for i in range(len(trips)):
        for j in range(i):
            if feasibleL1Merges[i, j] == False:
                feasibleL1Merges[i, j] = float('-inf')

    weightedList = []
    for i in range(len(trips)):
        for j in range(i):
            weightedList.append({'i': i, 'j': j, 'weight': feasibleL1Merges[i, j]})

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
                    newMerges.append({ 'trips': [trips[key]], 'distanceGain': 0})

            break

        # remove all items from weightedList where i or j have same values as in maxWeightItem
        i = maxWeightItem['i']
        j = maxWeightItem['j']

        tmpList = []
        for item in weightedList:
            if item['i'] != i and item['j'] != j:
                tmpList.append(item)

        weightedList = tmpList

        routeInfo = RouteStore().getRouteInfo2(trips[i]['pickup_location']['coordinates'], [ trips[i]['dropoff_location']['coordinates'], trips[j]['dropoff_location']['coordinates'] ])
        distanceGain = trips[i]['trip_distance'] + trips[j]['trip_distance'] - routeInfo['distance']

        if distanceGain > 0:
            newMerges.append({'trips': [trips[i], trips[j]], 'distanceGain': distanceGain})

            copiedIdxSet[i] = True
            copiedIdxSet[j] = True
        else:
            weightedList.append({'i': i, 'j': j, 'weight': distanceGain})

    return newMerges
