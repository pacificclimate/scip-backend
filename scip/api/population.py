from salmon_occurrence import ConservationUnit, Taxon, Reference, Population, Phenology
from sqlalchemy_sqlschema import maintain_schema
from sqlalchemy_sqlschema.sql import get_schema
from sqlalchemy import func


def population(
    session,
    overlap=None,
    common_name=None,
    scientific_name=None,
    subgroup=None,
    name=None,
):
    """Return information about salmon populations in the database that fulfill
    specified parameters.

    :param session: (sqlalchemy.orm.session.Session) a database Session object
    :param overlap: a WKT string specifying a geometry that overlaps with the desired populations
    :param common_name: common name of the salmon species of interest
    :param scientific_name: scientific name of the salmon species of interest
    :param subgroup: parameter designating a sub-species taxon, such as `lake` or `river` for sockeye salmon
    :param name: name of the conservation unit that encloses the population's range

    :return: a list of objects representing salmon populations that fulfill the given parameters. In
        addition to `common_name`, `scientific_name`, `subgroup`, and `name`, two geoJSON strings describing
        the geometry of the population7s extent are provided. `boundary` describes the outline of the extent,
        and `outlet` provides the most downstream point of the extent according to the RVIC routed flow data.

    """
    # TODO: verify input arguments

    # TODO: return additional data

    with maintain_schema("public, salmon_geometry", session):
        q = (
            session.query(
                Taxon.common_name.label("common_name"),
                Taxon.scientific_name.label("scientific_name"),
                Taxon.subgroup.label("subgroup"),
                ConservationUnit.name.label("name"),
                ConservationUnit.code.label("code"),
                func.ST_AsGeoJSON(ConservationUnit.boundary).label("boundary"),
                func.ST_ASGeoJSON(ConservationUnit.outlet).label("outlet"),
            )
            .join(Population, Population.conservation_unit_id == ConservationUnit.id)
            .join(Taxon, Population.taxon_id == Taxon.id)
        )

        if overlap:
            q = q.filter(ConservationUnit.boundary.ST_Intersects(overlap))

        if name:
            q = q.filter(ConservationUnit.name == name)

        if common_name:
            q = q.filter(Taxon.common_name == common_name)
        if scientific_name:
            q = q.filter(Taxon.scientific_name == scientific_name)
        if subgroup:
            q = q.filter(Taxon.subgroup == subgroup)

        results = q.all()

        result_list = [
            {
                att: getattr(result, att)
                for att in [
                    "common_name",
                    "scientific_name",
                    "subgroup",
                    "name",
                    "code",
                    "outlet",
                    "boundary",
                ]
            }
            for result in results
        ]

        def cu_dict(x):
            cu = {}
            for key in ["name", "code", "outlet", "boundary"]:
                val = x.pop(key)
                cu[key] = val
            x["conservation_unit"] = cu
            return x

        result_list = list(map(cu_dict, result_list))

        return result_list
