from salmon_occurrence import salmon_db, Region, Taxon, ConservationUnit, Population
import re
import json
import geojson
import shapely

## coordinates are in BC Albers projection, which is used by
# 3 this database. 2000000 1000000 us treated as an "origin"
## with the sample areas being squares displaced small distances
## from the origin.

# The database stores regions in BC Albers projection (for accuracy, and because
# all our sources are BC Albers). However, the front end that calls this API wants
# WGS84 projection for leaflet.
# Therefore the API does a translation from Albers to WGS84 using postgis
# functionality.
# But how can we check this translation?
# One option is to use OGR in the test suite to double-check the projections.
# However, that would make this repository dependant on GDAL, but only for testing
# this one task, which doesn't seem worth it. GDAL is fussy and difficult to
# maintain.
# Instead, here is a pregenerated list of all the points used in the test
# suite with their BC Albers and WGS84 translations.
# If you add new test data, you may need to add new points to this list, you can
# calculate them with gdaltransform -s_srs epsg:3005 -t_srs wgs84
# Points are ordered by x, then by y in the albers coordinate
albers_to_wgs84 = [
    [[2000000, 1000000], [-110.939153732, 53.046585944]],
    [[2000000, 1000010], [-110.939122171, 53.046673561]],
    [[2000000, 1000015], [-110.939106390, 53.046717369]],
    [[2000005, 1000005], [-110.939064899, 53.046620289]],
    [[2000005, 1000015], [-110.939033338, 53.046707906]],
    [[2000010, 1000000], [-110.939007627, 53.046567017]],
    [[2000010, 1000010], [-110.938976066, 53.046654634]],
    [[2000015, 1000000], [-110.938934575, 53.046557554]],
    [[2000015, 1000005], [-110.938918794, 53.046601362]],
    [[2000015, 1000015], [-110.938887232, 53.046688979]],
    [[2000015, 1000020], [-110.938944504, 53.046742251]],
    [[2000020, 1000015], [-110.938814180, 53.046679515]],
    [[2000020, 1000020], [-110.938798399, 53.046723324]],
    [[2000020, 1000030], [-110.938766837, 53.046810940]],
    [[2000030, 1000020], [-110.938652294, 53.046704396]],
    [[2000030, 1000030], [-110.938620731, 53.046792013]],
    [[2000100, 1000100], [-110.937377043, 53.047272831]],
    # because translatiing between albers and wgs84 sometimes
    # introduces rounding errors, points on the boundaries of
    # regions can be unreliable for overlap testing.
    # therefore, here are a few extra points inset by one meter
    # from the edges of boundaries, to use in overlap tests
    # to avoid pesky rounding errors.
    # (rounding errors aren't an issue with the way the server is
    # used in real life; the user is not going to click on the exact
    # edge of a region, and if they do, they will be unsurprised by
    # results that may exclude that region).
    [[2000014, 1000014], [-110.938904999, 53.046682110]],
    [[2000016, 1000016], [-110.938869466, 53.046695848]],
    [[2000021, 1000021], [-110.938780632, 53.046730193]],
]


def wgs84_point(x, y):
    for mapping in albers_to_wgs84:
        if x == mapping[0][0] and y == mapping[0][1]:
            return "POINT({} {})".format(mapping[1][0], mapping[1][1])
    assert 0, "cannot translate point {} {}, check albers_to_wgs84".format(x, y)


def wgs84_polygon(wkt):
    points = re.findall(r"[0-9\.]+ [0-9\.]+", wkt)

    def listize(str):
        p = str.split()
        return [int(p[0]), int(p[1])]

    def wgs84ize(p):
        for mapping in albers_to_wgs84:
            if p[0] == mapping[0][0] and p[1] == mapping[0][1]:
                return "{} {}".format(mapping[1][0], mapping[1][1])
        assert 0, "cannot translate polygon {}, check albers_to_wgs84".format(p)

    lpoints = list(map(listize, points))
    wgs_points = list(map(wgs84ize, lpoints))
    pol = "POLYGON(({}))".format(",".join(wgs_points))
    return pol


# square test regions.
# watersheds 1 and two overlap and are inside basin 1.
# watershed 3 is off by itself

WAT1 = {
    "kind": "watershed",
    "name": "Watershed 1",
    "code": "WAT1",
    "boundary": "POLYGON((2000000 1000000, 2000000 1000010, 2000010 1000010, 2000010 1000000, 2000000 1000000))",
    "outlet": "POINT(2000000 1000000)",
}

WAT2 = {
    "kind": "watershed",
    "name": "Watershed 2",
    "code": "WAT2",
    "boundary": "POLYGON((2000005 1000005, 2000005 1000015, 2000015 1000015, 2000015 1000005, 2000005 1000005))",
    "outlet": "POINT(2000005 1000005)",
}

WAT3 = {
    "kind": "watershed",
    "name": "Watershed 3",
    "code": "WAT3",
    "boundary": "POLYGON((2000020 1000020, 2000020 1000030, 2000030 1000030, 2000030 1000020, 2000020 1000020))",
    "outlet": "POINT(2000020 1000020)",
}

BAS1 = {
    "kind": "basin",
    "name": "Basin 1",
    "code": "BAS1",
    "boundary": "POLYGON((2000000 1000000, 2000000 1000015, 2000015 1000015, 2000015 1000000, 2000000 1000000))",
    "outlet": "POINT(2000000 1000000)",
}


# helper function that converts a no-srs wkt string to a
# geojson string with a BC Albers SRS
def make_albers(wkt):
    shape = shapely.wkt.loads(wkt)
    gj = json.loads(geojson.dumps(shape))
    gj["crs"] = {"type": "name", "properties": {"name": "epsg:3005"}}
    return json.dumps(gj)


# make a sample region into an ORM Region for database insertion
def make_region(kind, name, code, boundary, outlet):
    return Region(
        kind=kind,
        name=name,
        code=code,
        boundary=make_albers(boundary),
        outlet=make_albers(outlet),
    )


# this crude check just makes sure that all the Albers WKT points are in the
# APW's returned geojson object
def WKT_matches_geoJSON(wkt, gj):
    wkt_points = re.findall(r"[0-9\.]+ [0-9\.]+", wkt)

    def listize(str):
        p = str.split()
        return [int(p[0]), int(p[1])]

    wkt_points = list(map(listize, wkt_points))

    coords = json.loads(gj)["coordinates"][0]

    assert len(wkt_points) == len(coords)

    for point in wkt_points:
        wgs_point = False
        for mapping in albers_to_wgs84:
            if mapping[0][0] == point[0] and mapping[0][1] == point[1]:
                wgs_point = mapping[1]
        if not wgs_point:
            assert 0, "can't translate point {}, check albers_to_wgs84".format(point)

        assert wgs_point in coords


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


# salmon species
CHUM = {"common_name": "Chum", "scientific_name": "Oncorhynchus keta", "subgroup": None}

PNKO = {
    "common_name": "Pink",
    "scientific_name": "Oncorhynchus gorbuscha",
    "subgroup": "Odd",
}

PNKE = {
    "common_name": "Pink",
    "scientific_name": "Oncorhynchus gorbuscha",
    "subgroup": "Even",
}


# make a species into an ORM taxon for the database
def make_taxon(common_name, scientific_name, subgroup):
    return Taxon(
        common_name=common_name,
        scientific_name=scientific_name,
        subgroup=subgroup,
    )


# conservation units - 2 chum, and one for each pink group
# so we can test various combinations of species and area

# conservation units don't have a "kind" attribute in the database,
# it is included here so these constants can be used with check_regions()
CUC1 = {
    "kind": "conservation_unit",
    "name": "CU Chum 1",
    "code": "CUC1",
    "boundary": "POLYGON((2000000 1000000, 2000000 1000010, 2000010 1000010, 2000010 1000000, 2000000 1000000))",
    "outlet": "POINT(2000000 1000000)",
}

CUC2 = {
    "kind": "conservation_unit",
    "name": "CU Chum 2",
    "code": "CUC2",
    "boundary": "POLYGON((2000005 1000005, 2000005 1000015, 2000015 1000015, 2000015 1000005, 2000005 1000005))",
    "outlet": "POINT(2000005 1000005)",
}

CUPO = {
    "kind": "conservation_unit",
    "name": "CU Pink Odd",
    "code": "CUPO",
    "boundary": "POLYGON((2000020 1000020, 2000020 1000030, 2000030 1000030, 2000030 1000020, 2000020 1000020))",
    "outlet": "POINT(2000020 1000020)",
}

CUPE = {
    "kind": "conservation_unit",
    "name": "CU Pink Even",
    "code": "CUPE",
    "boundary": "POLYGON((2000000 1000000, 2000000 1000015, 2000015 1000015, 2000015 1000000, 2000000 1000000))",
    "outlet": "POINT(2000000 1000000)",
}


# make a sample conservation unit into an ORM CU for the database
def make_cu(name, code, boundary, outlet, kind):
    # kind argument is just ignored - used for verification only
    return ConservationUnit(
        name=name,
        code=code,
        boundary=make_albers(boundary),
        outlet=make_albers(outlet),
    )


# populations - 2 chum, one for each pink group
# in the database, the population  table mostly links to
# other tables, including phenology, taxon, and conservation_unit.
# these objects are used for data verification.

# chum population in CU CUC1
PCH1 = {"taxon": CHUM, "conservation_unit": CUC1}

# chum population in CU CUC2
PCH2 = {"taxon": CHUM, "conservation_unit": CUC2}

# Odd Year Pink population in CU CUPO
PPKO = {"taxon": PNKO, "conservation_unit": CUPO}

# Even year Pink population in CU CUPE
PPKE = {"taxon": PNKE, "conservation_unit": CUPE}


def make_population(taxon, conservation_unit):
    return Population(
        taxon_id=taxon.id,
        conservation_unit_id=conservation_unit.id,
        overwinter=False,
    )


# "expected" populations should be a list of taxon-conservation unit
# dicts, response is the object returned by the population API
def check_populations(expected, response):
    assert len(response) == len(expected)

    for exp_pop in expected:
        matched = False
        for res_pop in response:
            if (
                exp_pop["conservation_unit"]["code"]
                == res_pop["conservation_unit"]["code"]
            ):
                assert (
                    exp_pop["conservation_unit"]["name"]
                    == res_pop["conservation_unit"]["name"]
                )
                WKT_matches_geoJSON(
                    exp_pop["conservation_unit"]["boundary"],
                    res_pop["conservation_unit"]["boundary"],
                )
                assert exp_pop["taxon"]["common_name"] == res_pop["common_name"]
                assert exp_pop["taxon"]["scientific_name"] == res_pop["scientific_name"]
                assert exp_pop["taxon"]["subgroup"] == res_pop["subgroup"]
                matched = True
        assert matched, "Expected population {} not found in response".format(
            exp_pop["conservation_unit"]["code"]
        )
