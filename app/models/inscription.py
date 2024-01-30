from pydantic import BaseModel

class InscriptionPoste(BaseModel):
    festival_id: int
    poste: str
    jour: str
    creneau: str
    
class InscriptionZoneBenevole(BaseModel):
    festival_id: int
    poste: str
    zone_plan: str
    zone_benevole_id: str
    zone_benevole_name: str = ""
    jour: str
    creneau: str

class BatchInscriptionPoste(BaseModel):
    inscriptions: list[InscriptionPoste]
    desinscriptions: list[InscriptionPoste]
    
class BatchInscriptionZoneBenevole(BaseModel):
    inscriptions: list[InscriptionZoneBenevole]
    desinscriptions: list[InscriptionZoneBenevole]