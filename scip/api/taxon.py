from sqlalchemy_sqlschema import maintain_schema
from sqlalchemy_sqlschema.sql import get_schema
from salmon_occurrence import Taxon


def taxon(session):
    """Very simple API with no parameters. Returns a list of all salmon taxons in the
    database.

    :param session: (sqlalchemy.orm.session.Session) a database Session object

    :return: a list of objects representing salmon taxons in the database. A taxon has
        a scientific name, a common name, and optionall a subgroup.
    """
    q = session.query(
        Taxon.common_name.label("common_name"),
        Taxon.scientific_name.label("scientific_name"),
        Taxon.subgroup.label("subgroup"),
    )

    results = q.all()

    result_list = [
        {
            att: getattr(result, att)
            for att in ["common_name", "scientific_name", "subgroup"]
        }
        for result in results
    ]

    return result_list
