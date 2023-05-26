from salmon_occurrence import Region, ConservationUnit
from sqlalchemy_sqlschema import maintain_schema
from sqlalchemy_sqlschema.sql import get_schema
from sqlalchemy import func

def region(session, kind, overlap=None, name=None, code=None):

    with maintain_schema("public, salmon_geometry", session):
 
        #check kind
        if kind not in ["watershed", "basin", "conservation_unit"]:
            raise ValueError("Unsupported region kind: {}".format(kind))
        
        #TODO: check other arguments, especially overlap

        # conservation units and other types of region are kept seperately
        # in the databse, but we want them to have the same API access
        if kind == "conservation_unit":
            q = (
                session.query(
                    ConservationUnit.name.label("name"),
                    ConservationUnit.code.label("code"),
                    func.ST_AsGeoJSON(ConservationUnit.boundary).label("boundary"),
                    func.ST_ASGeoJSON(ConservationUnit.outlet).label("outlet")
                )
            )
            
            if overlap:
                q = q.filter(ConservationUnit.boundary.ST_Intersects(overlap))
                
            if name:
                q = q.filter(ConservationUnit.name == name)
                
            if code:
                q = q.filter(ConservationUnit.code == code)

        else:
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
            
            if overlap:
                q = q.filter(Region.boundary.ST_Intersects(overlap))
            
            if name:
                q = q.filter(Region.name == name)
                
            if code:
                q = q.filter(Region.code == code)


        results = q.all()
        
        result_list = []
        for result in results:
            res = {}
            res["name"] = getattr(result, "name")
            res["code"] = getattr(result, "code")
            res["kind"] = "conservation_unit" if (kind == "conservation_unit") else getattr(result, "kind")
            res["outlet"] = getattr(result, "outlet")
            res["boundary"] = getattr(result,"boundary")
            result_list.append(res)
        
        return(result_list)
