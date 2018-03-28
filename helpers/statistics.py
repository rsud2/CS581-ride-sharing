def getStatistics(mergedTrips):
    totalOriginalDistance = 0
    totalMergedDistance = 0

    for mergedTrip in mergedTrips:
        individualDistanceSum = 0
        mergedDistance = 0
        for trip in mergedTrip['trips']:
            individualDistanceSum += trip['trip_distance']

        mergedDistance = individualDistanceSum - mergedTrip['distanceGain']

        totalOriginalDistance += individualDistanceSum
        totalMergedDistance += mergedDistance

    return {'totalOriginalDistance': totalOriginalDistance, 'totalMergedDistance': totalMergedDistance}
