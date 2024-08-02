import pytest
from scip.api import population

# test data
from sample_data import PCH1, PCH2, PPKO, PPKE, check_populations, wgs84_point, wgs84_polygon


# check listing of all populations
def test_population_listing(db_populated_session):
    response = population(db_populated_session)
    check_populations([PCH1, PCH2, PPKO, PPKE], response)


# check listing by species
@pytest.mark.parametrize(
    "species,expected", [["Chum", [PCH1, PCH2]], ["Pink", [PPKO, PPKE]]]
)
def test_population_by_species(db_populated_session, species, expected):
    response = population(db_populated_session, common_name=species)
    check_populations(expected, response)


# check listing by subgroup
@pytest.mark.parametrize(
    "species,subgroup,expected",
    [
        ["Chum", None, [PCH1, PCH2]],
        ["Chum", "Banana", "error"],
        ["Chum", "Odd", "error"],
        ["Pink", "Odd", [PPKO]],
        ["Pink", "Even", [PPKE]],
        [None, "Even", "error"],
    ],
)
def test_population_by_subgroup(db_populated_session, species, subgroup, expected):
    if expected == "error":
        with pytest.raises(Exception) as e:
            response = population(
                db_populated_session, common_name=species, subgroup=subgroup
            )
    else:
        response = population(
            db_populated_session, common_name=species, subgroup=subgroup
        )
        check_populations(expected, response)


@pytest.mark.parametrize(
    "x,y,species,expected",
    [
        [2000000, 1000000, None, [PPKE, PCH1]],
        [2000000, 1000000, "Chum", [PCH1]],
        [2000014, 1000014, None, [PPKE, PCH2]],
        [2000014, 1000014, "Pink", [PPKE]],
        [2000100, 1000100, None, []],
        [2000021, 1000021, "Pink", [PPKO]],
        [2000021, 1000021, None, [PPKO]],
        [2000030, 1000030, "Chum", []],
    ],
)
def test_population_by_overlap_point(db_populated_session, x, y, species, expected):
    wkt = wgs84_point(x, y)
    response = population(db_populated_session, common_name=species, overlap=wkt)
    check_populations(expected, response)


@pytest.mark.parametrize(
    "species,expected",
    [
        [None, [PCH2, PPKO, PPKE]],
        ["Pink", [PPKO, PPKE]],
        ["Chum", [PCH2]],
        ["Banana", "error"],
    ],
)
def test_population_by_overlap_polygon(db_populated_session, species, expected):
    wkt = wgs84_polygon("POLYGON((2000014 1000014, 2000015 1000020, 2000021 1000021, 2000020 1000015, 2000014 1000014))")
    if expected == "error":
        with pytest.raises(Exception) as e:
            response = population(
                db_populated_session, common_name=species, overlap=wkt
            )
    else:
        response = population(db_populated_session, common_name=species, overlap=wkt)
        check_populations(expected, response)
