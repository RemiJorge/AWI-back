from pydantic import BaseModel

class Game(BaseModel):
    festival_id: int
    jeu_id: int
    nom_du_jeu: str
    auteur: str
    editeur: str
    nb_joueurs: str
    age_min: str
    duree: str
    type_jeu: str
    notice: str
    zone_plan: str
    zone_benevole: str
    zone_benevole_id: str
    a_animer: str
    recu: str
    mecanismes: str
    themes: str
    tags: str
    description: str
    image_jeu: str
    logo: str
    video: str