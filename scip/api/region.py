from salmon_occurrence import Region, ConservationUnit, Population, Taxon
from sqlalchemy_sqlschema import maintain_schema
from sqlalchemy_sqlschema.sql import get_schema
from sqlalchemy import func
from scip.api.validators import parse_region_kind, parse_common_name, parse_subgroup


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

        # This API runs four types of queries that take the same parameters
        # and return identically formatted results but are different "under
        # the hood." API requests may either target conservation units
        # (ConservationUnit table) or other kinds of region (Region table).
        # Requests may also either include species parameters (necessitating
        # a join to the Populations table for species info) or not specify
        # species parameters.
        # So code here has to separately handle
        #   1) Conservation units without species
        #   2) Conservation units with species
        #   3) Basin/watershed without species
        #   4) Basin/watershed with species

        if kind == "conservation_unit":
            if not common_name:
                # conservation unit without species
                q = session.query(
                    ConservationUnit.name.label("name"),
                    ConservationUnit.code.label("code"),
                    func.ST_AsGeoJSON(ConservationUnit.boundary).label("boundary"),
                    func.ST_ASGeoJSON(ConservationUnit.outlet).label("outlet"),
                    func.ST_Area(Region.boundary).label("area"),
                )
            else:
                # conservation unit with species - join to Population table
                # to get species presence data
                q = (
                    session.query(
                        ConservationUnit.name.label("name"),
                        ConservationUnit.code.label("code"),
                        func.ST_AsGeoJSON(ConservationUnit.boundary).label("boundary"),
                        func.ST_ASGeoJSON(ConservationUnit.outlet).label("outlet"),
                        func.ST_Area(Region.boundary).label("area"),
                    )
                    .join(
                        Population,
                        Population.conservation_unit_id == ConservationUnit.id,
                    )
                    .join(Taxon, Population.taxon_id == Taxon.id)
                    .filter(Taxon.common_name == common_name)
                )

                if subgroup:
                    q = q.filter(Taxon.subgroup == subgroup)
                q = q.distinct(ConservationUnit.name)

            # further optional filtering common to all conservation unit queries
            if overlap:
                q = q.filter(ConservationUnit.boundary.ST_Intersects(overlap))

            if name:
                q = q.filter(ConservationUnit.name == name)

            if code:
                q = q.filter(ConservationUnit.code == code)

        else:
            if not common_name:
                # watershed/basin without species
                q = session.query(
                    Region.name.label("name"),
                    Region.code.label("code"),
                    Region.kind.label("kind"),
                    func.ST_AsGeoJSON(Region.boundary).label("boundary"),
                    func.ST_AsGeoJSON(Region.outlet).label("outlet"),
                    func.ST_Area(Region.boundary).label("area"),
                ).filter(Region.kind == kind)
            else:
                # watershed/basin with species parameters - do a spatial
                # join with ConservationUnit, to access species info via
                # the 1:many ConservationUnit:Population relationship
                q = (
                    session.query(
                        Region.name.label("name"),
                        Region.code.label("code"),
                        Region.kind.label("kind"),
                        func.ST_AsGeoJSON(Region.boundary).label("boundary"),
                        func.ST_AsGeoJSON(Region.outlet).label("outlet"),
                        func.ST_Area(Region.boundary).label("area"),
                    )
                    .join(
                        ConservationUnit,
                        ConservationUnit.boundary.ST_Intersects(Region.boundary),
                    )
                    .join(
                        Population,
                        Population.conservation_unit_id == ConservationUnit.id,
                    )
                    .join(Taxon, Population.taxon_id == Taxon.id)
                    .filter(Region.kind == kind)
                    .filter(Taxon.common_name == common_name)
                )

                if subgroup:
                    q = q.filter(Taxon.subgroup == subgroup)
                q = q.distinct(Region.name)

            # further optional parameters common to all watershed/basin queries
            if overlap:
                q = q.filter(Region.boundary.ST_Intersects(overlap))

            if name:
                q = q.filter(Region.name == name)

            if code:
                q = q.filter(Region.code == code)

        results = q.all()

        result_list = [
            {
                att: getattr(result, att)
                for att in ["name", "code", "outlet", "boundary", "area"]
            }
            for result in results
        ]

        def assign_kind(x):
            x["kind"] = kind
            return x

        result_list = list(map(assign_kind, result_list))

        return result_list
