import pytest
import json

# API to test
from scip.api import region

# test data
from sample_data import WAT1, WAT2, WAT3, BAS1, check_regions


# test getting a list of all regions of a type
@pytest.mark.parametrize(
    "kind,expected",
    [("watershed", [WAT1, WAT2, WAT3]), ("basin", [BAS1]), ("conservation_unit", [])],
)
def test_region_listing(db_populated_session, kind, expected):
    response = region(db_populated_session, kind=kind)
    assert check_regions(expected, response)


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
    assert check_regions(expected, response)


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
    assert check_regions(expected, response)


# test requesting a region containing a point
@pytest.mark.parametrize(
    "x, y, kind, expected",
    [
        (0, 0, "watershed", [WAT1]),
        (0, 0, "basin", [BAS1]),
        (10, 10, "watershed", [WAT1, WAT2]),
    ],
)
def test_region_overlap_point(db_populated_session, x, y, kind, expected):
    wkt = "POINT({} {})".format(x, y)
    response = region(db_populated_session, kind=kind, overlap=wkt)
    assert check_regions(expected, response)


# test requestion a region overlapping a polygon
def test_region_overlap_polygon(db_populated_session):
    response = region(db_populated_session, kind="watershed", overlap=BAS1["boundary"])
    assert check_regions([WAT1, WAT2], response)
