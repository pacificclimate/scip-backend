from salmon_occurrence import salmon_db, Region, Taxon, ConservationUnit, Population
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
def make_region(kind, name, code, boundary, outlet):
    return Region(
        kind=kind,
        name=name,
        code=code,
        boundary=boundary,
        outlet=outlet,
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
    "boundary": "POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))",
    "outlet": "POINT(0 0)",
}

CUC2 = {
    "kind": "conservation_unit",
    "name": "CU Chum 2",
    "code": "CUC2",
    "boundary": "POLYGON((5 5, 5 15, 15 15, 15 5, 5 5))",
    "outlet": "POINT(5 5)",
}

CUPO = {
    "kind": "conservation_unit",
    "name": "CU Pink Odd",
    "code": "CUPO",
    "boundary": "POLYGON((20 20, 20 30, 30 30, 30 20, 20 20))",
    "outlet": "POINT(20 20)",
}

CUPE = {
    "kind": "conservation_unit",
    "name": "CU Pink Even",
    "code": "CUPE",
    "boundary": "POLYGON((0 0, 0 15, 15 15, 15 0, 0 0))",
    "outlet": "POINT(0 0)",
}


# make a sample conservation unit into an ORM CU for the database
def make_cu(name, code, boundary, outlet, kind):
    # kind argument is just ignored - used for verification only
    return ConservationUnit(
        name=name,
        code=code,
        boundary=boundary,
        outlet=outlet,
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
            if exp_pop["conservation_unit"]["code"] == res_pop["cu_code"]:
                assert exp_pop["conservation_unit"]["name"] == res_pop["cu_name"]
                WKT_matches_geoJSON(
                    exp_pop["conservation_unit"]["boundary"], res_pop["cu_boundary"]
                )
                assert exp_pop["taxon"]["common_name"] == res_pop["common_name"]
                assert exp_pop["taxon"]["scientific_name"] == res_pop["scientific_name"]
                assert exp_pop["taxon"]["subgroup"] == res_pop["subgroup"]
                matched = True
        assert matched, "Expected population {} not found in response".format(
            exp_pop["conservation_unit"]["code"]
        )
