from salmon_occurrence import Region, ConservationUnit, Population, Taxon
from sqlalchemy_sqlschema import maintain_schema
from sqlalchemy_sqlschema.sql import get_schema
from sqlalchemy import func
from scip.api.validators import parse_region_kind, parse_common_name, parse_subgroup
from scip.api.region_helpers import build_cu_query, build_region_query


def region(
    session, kind, overlap=None, name=None, code=None, common_name=None, subgroup=None
):
    """Return information about regions in the database that meet
    the specified parameters.

    :param session: (sqlalchemy.orm.session.Session) a database Session object
    :param kind: the type of region, such as `watershed`, `basin` or `conservation_unit`
    :param overlap: a WKT string specifying a geometry that overlaps with the desired region
    :param name: a string denoting the full name of the region
    :param code: a four letter unique code assigned to the region
    :param common_name: a salmon species - Chinook Chum, Coho, Pink, or Sockeye
    :param subgroup: a species subtype

    :return: a list of objects representing regions that fulfill all the specified criteria.
        For each region, the `kind`, `name`, and `code` are provided, along with two
        geoJSON objects representing the region's geometry: `boundary` describes the
        region's extent, and `outlet` is a geoJSON point representing the most downstream
        grid cell in the region, according to RVIC's flow model.

    """
    with maintain_schema("public, salmon_geometry", session):
        # check parameters
        kind = parse_region_kind(kind)
        if common_name:
            common_name = parse_common_name(common_name)
        if subgroup:
            subgroup = parse_subgroup(common_name, subgroup)

        # TODO: check overlap, see https://github.com/pacificclimate/scip-frontend/issues/43

        # This API presents data from multiple locations in the database, depending
        # on the values of the "kind" attribute. Some regions consist only of
        # geometry, like watersheds and basins, and are stored in the Region table.
        # Conservation units, on the other hand, are geometries associated with one or more
        # salmon populations, and are found in the ConservationUnit table.
        # To a user of the API, information about both these kinds of geometries
        # are accessed and formatted identically, but this functionality require
        # constructing parallel queries depending on which kin of geometry is
        # being asked about.

        if kind == "conservation_unit":
            q = build_cu_query(session, overlap, name, code, common_name, subgroup)
        else:
            q = build_region_query(
                session, kind, overlap, name, code, common_name, subgroup
            )
        results = q.all()

        result_list = [
            {
                att: getattr(result, att)
                for att in ["name", "code", "outlet", "boundary"]
            }
            for result in results
        ]

        def assign_kind(x):
            x["kind"] = kind
            return x

        result_list = list(map(assign_kind, result_list))

        return result_list
