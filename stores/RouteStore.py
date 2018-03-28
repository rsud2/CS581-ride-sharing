import urllib.request
import urllib.parse
import json


class RouteStore:

    __urlTemplate = 'http://localhost:5000/route/v1/driving/{0}'

    def getRouteInfo(self, tripStartLocation, waypoints):
        fragment = '{0},{1}'

        fragments = []
        fragments.append(fragment.format(tripStartLocation[0], tripStartLocation[1]))

        for waypoint in waypoints:
            fragments.append(fragment.format(waypoint[0], waypoint[1]))

        url = self.__urlTemplate.format(';'.join(fragments))
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request) as response:
            # TODO : error handling, response 'OK' checking, order of trips,
            # multiple trips should come in one array, etc
            # check waypoints for possibly more information??

            data = json.loads(response.read().decode())

            return {
                'first' : tripStartLocation,
                'waypoints' : waypoint,
                'distance': data['routes'][0]['distance'],
                'weight_name': data['routes'][0]['weight_name'],
                'weight': data['routes'][0]['weight']
            }
