# CS581-ride-sharing

Prerequisites : 
* Obtain OSM map files for New York : http://download.geofabrik.de/north-america/us/new-york-latest.osm.pbf 
* Install OSRM : https://github.com/Project-OSRM/osrm-backend/wiki/Docker-Recipes
* Install MongoDB : https://docs.mongodb.com/tutorials/install-mongodb-on-ubuntu/
* On the local MongoDB instance, create DB "trip_info", and within that, create collection "valid_trips" 
* Import data to MongoDB using data file valid_trips.json extracted from valid_trips.json.tar.gz file

Check : MongoDB and OSRM-backend are running on local machines on their default ports

Set configuration values used for different experiments in `config.py`

Run `main.py`
This should create a collection maned "stats" under the "trip_info" database

Sample query to get info from the stats collection : 

`db.getCollection('stats').aggregate([
    {
        $match: {'MAX_PASSENGER_COUNT' : <enter_passenger_count>, "USE_HEURISTICS": <boolean_value_as_needed>}
    }, {
        $group: {
            _id:{ 
              "WINDOW_SIZE": "$WINDOW_SIZE"
              , 'MAX_PASSENGER_COUNT': '$MAX_PASSENGER_COUNT'      
            }, 
            totalOriginalDistance: {$sum:"$totalOriginalDistance"},
            totalMergedDistance : {$sum:"$totalMergedDistance"},
            originalTripCount: {$sum:"$originalTripCount"},
            mergedTripCount: {$sum:"$mergedTripCount"},
            runningTime: {$avg:"$runningTime"},
            MAX_PASSENGER_COUNT: {$avg: "$MAX_PASSENGER_COUNT"},
            "WINDOW_SIZE": {$avg: "$WINDOW_SIZE"}
        }
    }, {
            
            $project: {
                distSaved: {$divide: [ {$subtract: ["$totalOriginalDistance", "$totalMergedDistance"]}, "$totalOriginalDistance"] },
                tripsSaved: {$divide: [ {$subtract: ["$originalTripCount", "$mergedTripCount"]}, "$originalTripCount"] },
                runningTime: "$runningTime",
                MAX_PASSENGER_COUNT: "$MAX_PASSENGER_COUNT",
                "WINDOW_SIZE": "$WINDOW_SIZE"
            }
            
        } 
])`
