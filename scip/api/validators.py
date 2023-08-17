# helper functions used to validate request parameters
import re
from salmon_occurrence import Region, ConservationUnit, Taxon
from sqlalchemy import func
from scip.api.taxon import taxon


def database_column_values(session, column):
    # returns a list for containing every value present in a specific
    # column in the database. Used to see if a user-supplied parameter
    # exists in the database.
    q = session.query(column).distinct().all()
    return list(map(lambda x: x[0], q))


def parse_region_kind(session, kind):
    k = kind.lower()
    kinds = database_column_values(session, Region.kind)
    kinds.append("conservation_unit")
    if k in kinds:
        return k
    else:
        raise ValueError(
            "Unsupported region kind: {}. Supported kinds: {}".format(kind, kinds)
        )


def parse_common_name(session, cn):
    species = database_column_values(session, Taxon.common_name)
    s = cn.lower().capitalize()
    if s in species:
        return s
    else:
        raise ValueError(
            "Unknown salmon species: {}. Known species: {}".format(s, species)
        )


def parse_subgroup(session, species, subgroup):
    taxons = taxon(session)

    sp = species.lower().capitalize()
    sg = subgroup.lower().capitalize()

    found = list(
        filter(lambda t: t["common_name"] == sp and t["subgroup"] == sg, taxons)
    )

    if len(found) > 0:
        return sg
    elif parse_common_name(session, sp):
        raise ValueError("Unknown subgroup of species {}: {}".format(sp, sg))
    else:
        raise ValueError("Unknown salmon species {}".format(species))


# This code has been taken out of use following the discovery that the
# front end sometimes passes geoJSON, which - absent WKT verification code -
# was not previously noticed. TODO: fix the front end, then return this check
# to use.
# https://github.com/pacificclimate/scip-frontend/issues/43


# we are expecting points or single polygons only here.
# it will need to be updated if the front end starts generating other
# shapes.
# wkt geometries may optionally have a space between the geometry type
# (like "POINT") and the opening parenthesis for the coordinate string.
# the front end doesn't generate WKT with a space, so it's not supported
# by this function, even though it is valid WKT.
def parse_wkt(wkt):
    regex_point = "-?(\d+(?:\.\d*)?) -?(\d+(?:\.\d*)?)"
    if wkt.startswith("POINT"):
        template = "^POINT\(" + regex_point + "\)$"
        print(template)
        if re.match(template, wkt):
            return wkt
        else:
            raise ValueError("Could not parse WKT POINT: {}".format(wkt))
    elif wkt.startswith("POLYGON"):
        template = (
            "^POLYGON\(\("
            + regex_point
            + ", "
            + regex_point
            + "(, "
            + regex_point
            + ")*\)\)$"
        )

        if re.match(template, wkt):
            return wkt
        else:
            raise ValueError("Could not parse WKT POLYGON: {}".format(wkt))
    else:
        raise ValueError(
            "Can't parse WKT, Only POINT and POLYGON geometries are supported. {}".format(
                wkt
            )
        )
