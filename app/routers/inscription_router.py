from fastapi import APIRouter, Security
from typing import Annotated
from ..controllers.auth_controller import verify_token
from ..controllers.inscription_controller import (
    inscription_user_poste, 
    inscription_user_zone_benevole, 
    desinscription_user_poste, 
    desinscription_user_zone_benevole, 
    get_nb_inscriptions_poste, 
    get_nb_inscriptions_zone_benevole,
    auto_assign_flexibles_to_postes,
    auto_assign_flexibles_to_zones_benevoles
    )
from ..models.user import User
from ..models.inscription import InscriptionPoste, InscriptionZoneBenevole


inscription_router = APIRouter(
    prefix="/inscription",
    tags=["inscription"],
)


@inscription_router.post("/poste", response_model=dict, description="Inscription a un poste")
async def inscription_poste(inscription: InscriptionPoste, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await inscription_user_poste(user, inscription)


@inscription_router.post("/zone-benevole", response_model=dict, description="Inscription a une zone benevole")
async def inscription_zone_benevole(inscription: InscriptionZoneBenevole, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await inscription_user_zone_benevole(user, inscription)


@inscription_router.delete("/poste", response_model=dict, description="Desinscription a un poste")
async def desinscription_poste(inscription: InscriptionPoste, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await desinscription_user_poste(user, inscription)


@inscription_router.delete("/zone-benevole", response_model=dict, description="Desinscription a une zone benevole")
async def desinscription_zone_benevole(inscription: InscriptionZoneBenevole, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await desinscription_user_zone_benevole(user, inscription)


@inscription_router.get("/poste", response_model=list, description="Get all inscriptions poste numbers by day and creneau")
async def get_nb_inscriptions_poste_route(user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await get_nb_inscriptions_poste()


@inscription_router.get("/zone-benevole", response_model=list, description="Get all inscriptions zone benevole numbers by day and creneau")
async def get_nb_inscriptions_zone_benevole_route(user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await get_nb_inscriptions_zone_benevole()


@inscription_router.put("/poste/auto-assign-flexibles", response_model=dict, description="Auto assign flexibles to postes")
async def auto_assign_flexibles_to_postes_route(user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await auto_assign_flexibles_to_postes()


@inscription_router.put("/zone-benevole/auto-assign-flexibles", response_model=dict, description="Auto assign flexibles to zones benevoles")
async def auto_assign_flexibles_to_zones_benevoles_route(user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await auto_assign_flexibles_to_zones_benevoles()
