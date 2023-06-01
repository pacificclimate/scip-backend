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
    # TODO: verify input arguments

    # TODO: return additional data

    with maintain_schema("public, salmon_geometry", session):
        q = (
            session.query(
                Taxon.common_name.label("common_name"),
                Taxon.scientific_name.label("scientific_name"),
                Taxon.subgroup.label("subgroup"),
                ConservationUnit.name.label("cu_name"),
                ConservationUnit.code.label("cu_code"),
                func.ST_AsGeoJSON(ConservationUnit.boundary).label("cu_boundary"),
                func.ST_ASGeoJSON(ConservationUnit.outlet).label("cu_outlet"),
            )
            .join(Population, Population.conservation_unit_id == ConservationUnit.id)
            .join(Taxon, Population.taxon_id == Taxon.id)
        )

        if overlap:
            q = q.filter(ConservationUnit.boundary.ST_Intersects(overlap))

        if name:
            q = q.filter(ConservationUnit.name == name)

        # TODO: more sophisticated handling of subgroups here
        if common_name:
            q = q.filter(Taxon.common_name == common_name)
        if scientific_name:
            q = q.filter(Taxon.scientific_name == scientific_name)
        if subgroup:
            q = q.filter(Taxon.subgroup == subgroup)

        results = q.all()

        result_list = []
        for result in results:
            res = {}
            for att in [
                "common_name",
                "scientific_name",
                "subgroup",
                "cu_name",
                "cu_code",
                "cu_outlet",
                "cu_boundary",
            ]:
                res[att] = getattr(result, att)
            result_list.append(res)

        return result_list
