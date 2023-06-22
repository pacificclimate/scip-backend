from salmon_occurrence import Region, ConservationUnit
from sqlalchemy_sqlschema import maintain_schema
from sqlalchemy_sqlschema.sql import get_schema
from sqlalchemy import func


def region(session, kind, overlap=None, name=None, code=None):
    """Return information about regions in the database that meet
    the specified parameters.

    :param session: (sqlalchemy.orm.session.Session) a database Session object
    :param kind: the type of region, such as `watershed`, `basin` or `conservation_unit`
    :param overlap: a WKT string specifying a geometry that overlaps with the desired region
    :param name: a string denoting the full name of the region
    :param code: a four letter unique code assigned to the region

    :return: a list of objects representing regions that fulfill the specified criteria.
        For each region, the `kind`, `name`, and `code` are provided, along with two
        geoJSON objects representing the region's geometry: `boundary` describes the
        region's extent, and `outlet` is a geoJSON point representing the most downstream
        grid cell in the region, according to RVIC's flow model.

    """
    with maintain_schema("public, salmon_geometry", session):
        # check kind
        if kind not in ["watershed", "basin", "conservation_unit"]:
            raise ValueError("Unsupported region kind: {}".format(kind))

        # TODO: check other arguments, especially overlap

        # conservation units and other types of region are kept seperately
        # in the databse, but we want them to have the same API access
        if kind == "conservation_unit":
            q = session.query(
                ConservationUnit.name.label("name"),
                ConservationUnit.code.label("code"),
                func.ST_AsGeoJSON(ConservationUnit.boundary).label("boundary"),
                func.ST_ASGeoJSON(ConservationUnit.outlet).label("outlet"),
            )

            if overlap:
                q = q.filter(ConservationUnit.boundary.ST_Intersects(overlap))

            if name:
                q = q.filter(ConservationUnit.name == name)

            if code:
                q = q.filter(ConservationUnit.code == code)

        else:
            q = session.query(
                Region.name.label("name"),
                Region.code.label("code"),
                Region.kind.label("kind"),
                func.ST_AsGeoJSON(Region.boundary).label("boundary"),
                func.ST_AsGeoJSON(Region.outlet).label("outlet"),
            ).filter(Region.kind == kind)

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
                for att in [
                    "name",
                    "code",
                    "outlet",
                    "boundary",
                ]
            }
            for result in results
        ]

        def assign_kind(x):
            x["kind"] = kind
            return x

        result_list = list(map(assign_kind, result_list))

        return result_list
