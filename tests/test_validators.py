import pytest
from scip.api.validators import (
    parse_region_kind,
    parse_common_name,
    parse_subgroup,
    parse_wkt,
)
from sample_data import WAT1, WAT2, WAT3, BAS1


@pytest.mark.parametrize(
    "kind,expected",
    [
        ("Basin", "basin"),
        ("basin", "basin"),
        ("watershed", "watershed"),
        ("banana", "error"),
    ],
)
def test_parsing_regions(db_populated_session, kind, expected):
    if expected is "error":
        with pytest.raises(ValueError) as e:
            parse_region_kind(db_populated_session, kind)
    else:
        assert parse_region_kind(db_populated_session, kind) == expected


@pytest.mark.parametrize(
    "species,expected",
    [
        ("Chum", "Chum"),
        ("pink", "Pink"),
        ("Chummmm", "error"),
        ("Banana", "error"),
        ("489", "error"),
    ],
)
def test_parsing_species(db_populated_session, species, expected):
    if expected is "error":
        with pytest.raises(ValueError) as e:
            parse_common_name(db_populated_session, species)
    else:
        assert parse_common_name(db_populated_session, species) == expected


@pytest.mark.parametrize(
    "species,subgroup,expected",
    [
        ("Pink", "Odd", "Odd"),
        ("Pink", "odd", "Odd"),
        ("Pink", "even", "Even"),
        ("Chum", "Even", "error"),
        ("Pink", "Lake", "error"),
        ("Pink", "Banana", "error"),
        ("Chum", "Banana", "error"),
    ],
)
def test_parsing_subgroups(db_populated_session, species, subgroup, expected):
    if expected is "error":
        with pytest.raises(ValueError) as e:
            parse_subgroup(db_populated_session, species, subgroup)
    else:
        assert parse_subgroup(db_populated_session, species, subgroup) == expected


@pytest.mark.parametrize("region", [WAT1, WAT2, WAT3, BAS1])
def test_parsing_wkt_polygons(region):
    assert region["boundary"] == parse_wkt(region["boundary"])


@pytest.mark.parametrize("region", [WAT1, WAT2, WAT3, BAS1])
def test_parsing_wkt_points(region):
    assert region["outlet"] == parse_wkt(region["outlet"])


@pytest.mark.parametrize(
    "bad_wkt",
    [
        "POINT",
        "BANANA",
        "BANANA(0 0)",
        "POINT()",
        "POINT(0 0 0 0)",
        "POINT(0)",
        "POLYGON((5 5 5 15, 15 15, 15 5, 5 5))",
        "POINT(BANANA BANANA)",
        "POINT(5 BANANA)"
        "POLYGON()"
        "POLYGON(())"
        "POLYGON((5 5, 5 15))"
        "POLYGON ((5 5, 5 15, 15 15, 15 5, 5 5))",
    ],
)
def test_parsing_invalid_wkt(bad_wkt):
    with pytest.raises(ValueError) as e:
        parse_wkt(bad_wkt)
