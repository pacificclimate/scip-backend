import pytest
from scip.api import population

# test data
from sample_data import PCH1, PCH2, PPKO, PPKE, check_populations


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
        [0, 0, None, [PPKE, PCH1]],
        [0, 0, "Chum", [PCH1]],
        [15, 15, None, [PPKE, PCH2]],
        [15, 15, "Pink", [PPKE]],
        [100, 100, None, []],
        [30, 30, "Pink", [PPKO]],
        [30, 30, None, [PPKO]],
        [30, 30, "Chum", []],
    ],
)
def test_population_by_overlap_point(db_populated_session, x, y, species, expected):
    wkt = "POINT({} {})".format(x, y)
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
    wkt = "POLYGON((15 15, 15 20, 20 20, 20 15, 15 15))"
    if expected == "error":
        with pytest.raises(Exception) as e:
            response = population(
                db_populated_session, common_name=species, overlap=wkt
            )
    else:
        response = population(db_populated_session, common_name=species, overlap=wkt)
        check_populations(expected, response)
