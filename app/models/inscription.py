from pydantic import BaseModel

class InscriptionPoste(BaseModel):
    poste: str
    jour: str
    creneau: str
    
class InscriptionZoneBenevole(BaseModel):
    poste: str
    zone_plan: str
    zone_benevole_id: str
    zone_benevole_name: str = ""
    jour: str
    creneau: str
