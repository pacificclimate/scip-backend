from salmon_occurrence import Region, ConservationUnit
from sqlalchemy_sqlschema import maintain_schema
from sqlalchemy_sqlschema.sql import get_schema
from sqlalchemy import func

def region(session, kind, name=None, code=None):
    print("region call")

    with maintain_schema("public, salmon_geometry", session):
#        stmt = get_schema()
#        print(stmt)
 
        #check kind
        if kind not in ["watershed", "basin", "conservation_unit"]:
            raise ValueError("Unsupported region kind: {}".format(kind))
        
    
        if kind == "conservation_unit":
            print("conservation unit table")
            q = (
                session.query(
                    ConservationUnit.name.label("name"),
                    ConservationUnit.code.label("code"),
                    func.ST_AsGeoJSON(ConservationUnit.boundary).label("boundary"),
                    func.ST_ASGeoJSON(ConservationUnit.outlet).label("outlet")
                )
            )

        else:
            print("Region table")
            q = (
                session.query(
                    Region.name.label("name"),
                    Region.code.label("code"),
                    Region.kind.label("kind"),
                    func.ST_AsGeoJSON(Region.boundary).label("boundary"),
                    func.ST_AsGeoJSON(Region.outlet).label("outlet")
                )
                .filter(Region.kind == kind)
            )
        

        results = q.all()
        print(results)    
        
        result_list = []
        for result in results:
            res = {}
            res["name"] = getattr(result, "name")
            res["code"] = getattr(result, "code")
            res["kind"] = "conservation_unit" if (kind == "conservation_unit") else getattr(result, "kind")
            res["outlet"] = getattr(result, "outlet")
            res["boundary"] = getattr(result,"boundary")
            result_list.append(res)
        
        print(result_list)
        return(result_list)
