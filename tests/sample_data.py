from salmon_occurrence import salmon_db, Region
import re
import json


# square test regions.
# watersheds 1 and two overlap and are inside basin 1.
# watershed 3 is off by itself

WAT1 = {
    "kind": "watershed",
    "name": "Watershed 1",
    "code": "WAT1",
    "boundary": "POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))",
    "outlet": "POINT(0 0)",
}

WAT2 = {
    "kind": "watershed",
    "name": "Watershed 2",
    "code": "WAT2",
    "boundary": "POLYGON((5 5, 5 15, 15 15, 15 5, 5 5))",
    "outlet": "POINT(5 5)",
}

WAT3 = {
    "kind": "watershed",
    "name": "Watershed 3",
    "code": "WAT3",
    "boundary": "POLYGON((20 20, 20 30, 30 30, 30 20, 20 20))",
    "outlet": "POINT(20 20)",
}

BAS1 = {
    "kind": "basin",
    "name": "Basin 1",
    "code": "BAS1",
    "boundary": "POLYGON((0 0, 0 15, 15 15, 15 0, 0 0))",
    "outlet": "POINT(0 0)",
}


# make a sample region into an ORM Region for database insertion
def make_region(params):
    return Region(
        kind=params["kind"],
        name=params["name"],
        code=params["code"],
        boundary=params["boundary"],
        outlet=params["outlet"],
    )


# this crude check just makes sure that all the WKT points are in the
# geojson object; it doesn't fuss with order
# (because I'm not sure postGIS preserves it)
def WKT_matches_geoJSON(wkt, gj):
    wkt_points = re.findall(r"[0-9\.]+ [0-9\.]+", wkt)

    def listize(str):
        p = str.split()
        return [int(p[0]), int(p[1])]

    wkt_points = list(map(listize, wkt_points))
    print(wkt_points)

    coords = json.loads(gj)["coordinates"][0]

    assert len(wkt_points) == len(coords)

    for point in wkt_points:
        assert point in coords


# check that the specified regions (and no others) were return by the API
def check_regions(expected, response):
    assert len(response) == len(expected)

    for exp_reg in expected:
        matched = False
        for res_reg in response:
            if res_reg["code"] == exp_reg["code"]:
                assert res_reg["kind"] == exp_reg["kind"]
                assert res_reg["name"] == exp_reg["name"]
                WKT_matches_geoJSON(exp_reg["boundary"], res_reg["boundary"])
                matched = True
        assert matched, "Expected region {} not found in response".format(
            exp_reg["code"]
        )
    return True
