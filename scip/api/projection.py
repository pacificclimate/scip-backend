# The postGIS database is in the BC Albers projection. The front end uses no
# particular projection, but we assume it to be EPSG 4326 for convenience
# functions in this file convert between the two systems.

# use assume_4326 on parameters received from the front end, to add a projection
# use to_4326 on data fetched from the back end, to convert it to EPSG 4236

from sqlalchemy import func
import shapely.wkt
import geojson
import json


def to_4326(geom):
    """convert a geometry to 4326 to send to the front end"""
    return func.ST_Transform(geom, 4326)


def assume_4326(wkt):
    """convert a WKT string (no projection) to an equivalent geoJSON string in WPSG 4326"""
    shape = shapely.wkt.loads(wkt)
    gj = json.loads(geojson.dumps(shape))
    gj["crs"] = {"type": "name", "properties": {"name": "epsg:4326"}}

    return json.dumps(gj)
