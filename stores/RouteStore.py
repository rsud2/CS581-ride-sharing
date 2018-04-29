import urllib.request
import urllib.parse
import json

import itertools

from joblib import Parallel, delayed


class RouteStore:

    __urlTemplate = 'http://localhost:5000/{0}/v1/driving/{1}'

    def __buildResult(self, data, tripStartLocation, waypoints):
        return {
            'first': tripStartLocation,
            'waypoints': waypoints,
            # TODO : picking routing info for the first alternative. pick one with best metrics
            'distance': data['routes'][0]['distance'] / 1000,
            'weight_name': data['routes'][0]['weight_name'],
            'weight': data['routes'][0]['weight']
        }

    def __getUrl(self, tripStartLocation, waypoints, type='route'):
        fragment = '{0},{1}'
        fragments = []
        fragments.append(fragment.format(tripStartLocation[0], tripStartLocation[1]))
        for waypoint in waypoints:
            fragments.append(fragment.format(waypoint[0], waypoint[1]))
        url = self.__urlTemplate.format(type, ';'.join(fragments))
        return url

    def __getRoute(self, request, tripStartLocation, waypoints):
        with urllib.request.urlopen(request) as response:
            # TODO : error handling, response 'OK' checking, order of trips,
            # multiple trips should come in one array, etc
            # check waypoints for possibly more information??

            data = json.loads(response.read().decode())

            return data

    def getRouteInfo(self, tripStartLocation, waypoints, type='route'):

        url= self.__getUrl(tripStartLocation, waypoints, type)
        request = urllib.request.Request(url)
        response = self.__getRoute(request, tripStartLocation, waypoints)
        return self.__buildResult(response, tripStartLocation, waypoints)


    def __routeOne(self, tuple):
        start, waypoints = tuple
        return self.getRouteInfo(start, waypoints)

    def getRouteInfo2(self, tripStartLocation, waypoints):
        alternatives = list(itertools.permutations(waypoints))

        options = []
        for alt in alternatives:
            options.append((tripStartLocation, alt))

        results = Parallel(n_jobs=-1, backend="threading")(
        delayed(self.__routeOne)(opt) for opt in options)
        return sorted(results, key=lambda k: k['distance'])[0]

    def getRouteInfo3(self, tripStartLocation, waypoints):

        url= self.__getUrl(tripStartLocation, waypoints, 'trip')
        request = urllib.request.Request(url)
        response = self.__getRoute(request, tripStartLocation, waypoints)

        newWaypoints = []
        for waypoint in sorted(response['waypoints'], key= lambda k: k['waypoint_index']):
            newWaypoints.append(([waypoint['location'][0], waypoint['location'][1]]))

        url= self.__getUrl(tripStartLocation, waypoints, 'route')
        request = urllib.request.Request(url)
        response = self.__getRoute(request, tripStartLocation, newWaypoints)

        return self.__buildResult(response, tripStartLocation, newWaypoints)
