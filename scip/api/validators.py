# helper functions used to validate request parameters
import re


def parse_region_kind(kind):
    k = kind.lower()
    kinds = ["basin", "watershed", "conservation_unit"]
    if k in kinds:
        return k
    else:
        raise ValueError(
            "Unsupported region kind: {}. Supported kinds: {}".format(kind, kinds)
        )


def parse_common_name(cn):
    species = ["Chinook", "Chum", "Coho", "Pink", "Sockeye"]
    s = cn.lower().capitalize()
    if s in species:
        return s
    else:
        raise ValueError(
            "Unknown salmon species: {}. Known species: {}".format(s, species)
        )


def parse_subgroup(species, subgroup):
    subgroups = {"Odd": "Pink", "Even": "Pink", "Lake": "Sockeye", "River": "Sockeye"}
    sg = subgroup.lower().capitalize()

    if sg in subgroups and subgroups[sg] == species:
        return sg
    elif species in subgroups.values():
        raise ValueError("Unknown subgroup of species {}: {}".format(species, sg))
    elif species in ["Chinook", "Chum", "Coho"]:
        raise ValueError("No subgroups for {} are known".format(species))
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
