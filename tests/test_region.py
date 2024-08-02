import pytest
import json
from scip.api import region

# test data
from sample_data import (
    WAT1,
    WAT2,
    WAT3,
    BAS1,
    check_regions,
    wgs84_point,
    wgs84_polygon,
)
from sample_data import CUC1, CUC2, CUPO, CUPE


# test getting a list of all regions of a type
@pytest.mark.parametrize(
    "kind,expected",
    [
        ("watershed", [WAT1, WAT2, WAT3]),
        ("basin", [BAS1]),
        ("conservation_unit", [CUC1, CUC2, CUPO, CUPE]),
    ],
)
def test_region_listing(db_populated_session, kind, expected):
    response = region(db_populated_session, kind=kind)
    check_regions(expected, response)


# test a nonexistant type
def test_bad_kind(db_populated_session):
    with pytest.raises(ValueError):
        region(db_populated_session, kind="banana")


# test requesting a region by code
@pytest.mark.parametrize(
    "code,kind,expected",
    [
        ("WAT1", "watershed", [WAT1]),
        ("WAT2", "watershed", [WAT2]),
        ("BAS1", "watershed", []),
        ("BAS1", "basin", [BAS1]),
        ("BANANA", "watershed", []),
    ],
)
def test_region_code_parameter(db_populated_session, code, kind, expected):
    response = region(db_populated_session, kind=kind, code=code)
    check_regions(expected, response)


# test requesting a region by name
@pytest.mark.parametrize(
    "name, kind, expected",
    [
        ("Watershed 1", "watershed", [WAT1]),
        ("Banana", "watershed", []),
        ("Basin 1", "basin", [BAS1]),
    ],
)
def test_region_name_parameter(db_populated_session, name, kind, expected):
    response = region(db_populated_session, kind=kind, name=name)
    check_regions(expected, response)


# test requesting a region containing a point
@pytest.mark.parametrize(
    "x, y, kind, expected",
    [
        (2000000, 1000000, "watershed", [WAT1]),
        (2000000, 1000000, "basin", [BAS1]),
        (2000005, 1000005, "watershed", [WAT1, WAT2]),
        (2000000, 1000000, "conservation_unit", [CUC1, CUPE]),
    ],
)
def test_region_overlap_point(db_populated_session, x, y, kind, expected):
    wkt = wgs84_point(x, y)
    response = region(db_populated_session, kind=kind, overlap=wkt)
    check_regions(expected, response)


# test requestion a region overlapping a polygon
def test_region_overlap_polygon(db_populated_session):
    response = region(
        db_populated_session, kind="watershed", overlap=wgs84_polygon(BAS1["boundary"])
    )
    check_regions([WAT1, WAT2], response)


@pytest.mark.parametrize(
    "species,subgroup,kind,expected",
    [
        ("Pink", "Odd", "conservation_unit", [CUPO]),
        ("Pink", "Even", "conservation_unit", [CUPE]),
        ("Pink", None, "conservation_unit", [CUPO, CUPE]),
        ("Pink", "Odd", "basin", []),
        ("Pink", "Even", "basin", [BAS1]),
        ("Chum", None, "conservation_unit", [CUC1, CUC2]),
        ("Chum", None, "watershed", [WAT1, WAT2]),
    ],
)
def test_region_by_species(db_populated_session, species, subgroup, kind, expected):
    response = region(
        db_populated_session, kind=kind, common_name=species, subgroup=subgroup
    )
    check_regions(expected, response)


@pytest.mark.parametrize(
    "species,subgroup,boundary,kind,expected",
    [
        ("Pink", "Odd", WAT1, "watershed", []),
        ("Pink", "Odd", WAT3, "watershed", [WAT3]),
        ("Pink", "Even", WAT1, "watershed", [WAT1, WAT2]),
        ("Pink", "Even", WAT1, "basin", [BAS1]),
    ],
)
def test_region_by_species_and_overlap(
    db_populated_session, species, subgroup, boundary, kind, expected
):
    response = region(
        db_populated_session,
        kind=kind,
        common_name=species,
        subgroup=subgroup,
        overlap=wgs84_polygon(boundary["boundary"]),
    )
    check_regions(expected, response)
