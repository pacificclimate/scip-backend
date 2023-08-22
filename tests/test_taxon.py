import pytest
import json
from scip.api import taxon
from sample_data import CHUM, PNKO, PNKE


# taxon only does one thing and accepts no parameters,
# testing it is not very complicated.
def test_taxon_listing(db_populated_session):
    response = taxon(db_populated_session)
    expected_taxons = [CHUM, PNKO, PNKE]
    assert (len(response)) == len(expected_taxons)
    for t in expected_taxons:
        matched = False
        for r in response:
            if (
                r["common_name"] == t["common_name"]
                and r["subgroup"] == t["subgroup"]
                and r["scientific_name"] == t["scientific_name"]
            ):
                matched = True
        assert matched == True, "Expected salmon taxon not found: {}".format(t)
