"""
The functions in this file assist the region API to build queries
needed to provide information about "regions" (polygons) in the postGIS
database. The polygons are stored in two different tables in the database,
Regions and ConservationUnits, but are presented identically to the user.

Additionally, the API user may specify that they only wish to see regions
in which certain species of salmon are found. The two geometry-recording
tables have different relationships to the Population table, which records
salmon information. Therefore, there are four possible types of queries
that might need to be constructed:
 1. conservation unit with species: build_cu_query -> cu_with_taxon
 2. conservation unit without species: build_cu_query -> cu_geometry_only
 3. other region with species: build_region_query -> region_with_taxon
 4. other region without species: build_region_query -> region_geometry_only
"""

from salmon_occurrence import Region, ConservationUnit, Population, Taxon
from sqlalchemy import func
from scip.api.projection import to_4326, assume_4326


def cu_with_taxon(session, common_name, subgroup):
    """Returns a query that joins the conservation unit table
    with the population table, in order to get a list of
    conservation units that contain a particular salmon species"""
    q = cu_geometry_only(session)

    q = q.join(
        Population,
        Population.conservation_unit_id == ConservationUnit.id,
    )
    q = q.join(Taxon, Population.taxon_id == Taxon.id)
    q = q.filter(Taxon.common_name == common_name)

    if subgroup:
        q = q.filter(Taxon.subgroup == subgroup)
    q = q.distinct()

    return q


def cu_geometry_only(session):
    """Returns a simple query on the conservation unit table"""
    q = session.query(
        ConservationUnit.name.label("name"),
        ConservationUnit.code.label("code"),
        func.ST_AsGeoJSON(to_4326(ConservationUnit.boundary)).label("boundary"),
        func.ST_ASGeoJSON(to_4326(ConservationUnit.outlet)).label("outlet"),
    )

    return q


def build_cu_query(
    session, overlap=None, name=None, code=None, common_name=None, subgroup=None
):
    """Creates an SQLalchemy query to get information about
    conservation units"""
    if common_name:
        q = cu_with_taxon(session, common_name, subgroup)
    else:
        q = cu_geometry_only(session)

    if overlap:
        q = q.filter(
            to_4326(ConservationUnit.boundary).ST_Intersects(assume_4326(overlap))
        )

    if name:
        q = q.filter(ConservationUnit.name == name)

    if code:
        q = q.filter(ConservationUnit.code == code)

    return q


def region_with_taxon(session, kind, common_name, subgroup):
    """Returns a query that spatially joins the regions table with the
    conservation units table, in order to access salmon population info"""
    q = region_geometry_only(session, kind)
    q = q.join(
        ConservationUnit,
        ConservationUnit.boundary.ST_Intersects(Region.boundary),
    )
    q = q.join(
        Population,
        Population.conservation_unit_id == ConservationUnit.id,
    )
    q = q.join(Taxon, Population.taxon_id == Taxon.id)
    q = q.filter(Taxon.common_name == common_name)

    if subgroup:
        q = q.filter(Taxon.subgroup == subgroup)
    q = q.distinct()

    return q


def region_geometry_only(session, kind):
    """Returns a simple query on the regions table"""
    q = session.query(
        Region.name.label("name"),
        Region.code.label("code"),
        Region.kind.label("kind"),
        func.ST_AsGeoJSON(to_4326(Region.boundary)).label("boundary"),
        func.ST_AsGeoJSON(to_4326(Region.outlet)).label("outlet"),
    ).filter(Region.kind == kind)

    return q


def build_region_query(
    session, kind, overlap=None, name=None, code=None, common_name=None, subgroup=None
):
    """Creates and SQLAlchemy query to get information about watersheds or basins"""
    if common_name:
        q = region_with_taxon(session, kind, common_name, subgroup)
    else:
        q = region_geometry_only(session, kind)

    if overlap:
        q = q.filter(to_4326(Region.boundary).ST_Intersects(assume_4326(overlap)))

    if name:
        q = q.filter(Region.name == name)

    if code:
        q = q.filter(Region.code == code)

    return q
