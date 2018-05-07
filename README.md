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

For a sample query to get info from the stats collection see sample_stats_query.txt
