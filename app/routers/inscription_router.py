from fastapi import APIRouter, Security
from typing import Annotated
from pydantic import BaseModel
from ..controllers.auth_controller import verify_token
from ..controllers.inscription_controller import (
    inscription_user_poste, 
    inscription_user_zone_benevole, 
    desinscription_user_poste, 
    desinscription_user_zone_benevole, 
    get_nb_inscriptions_poste, 
    get_nb_inscriptions_zone_benevole,
    auto_assign_flexibles_to_postes,
    auto_assign_flexibles_to_zones_benevoles,
    batch_inscription_poste,
    batch_inscription_zone_benevole,
    #get_postes_inscriptions_user,
    #get_zones_benevoles_inscriptions_user
    get_inscriptions_poste,
    get_inscriptions_zone_benevole,
    assign_user_to_poste,
    delete_user_to_poste,
    delete_user_to_zone_benevole,
    get_flexibles
    )
from ..models.user import User
from ..models.inscription import InscriptionPoste, InscriptionZoneBenevole, BatchInscriptionPoste, BatchInscriptionZoneBenevole, AssignInscriptionPoste, AssignInscriptionZoneBenevole
from ..models.message import MessageSendEveryone, MessageSend
from ..controllers.message_controller import send_message_to_everyone, send_message
from ..controllers.festival_controller import get_active_festival


inscription_router = APIRouter(
    prefix="/inscription",
    tags=["inscription"],
)

class FlexiblesQuery(BaseModel):
    festival_id: int
    jour: str = ""
    creneau: str = ""


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
async def get_nb_inscriptions_postes_route(festival_id: int, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await get_nb_inscriptions_poste(user.user_id, festival_id)


@inscription_router.get("/zone-benevole", response_model=list, description="Get all inscriptions zone benevole numbers by day and creneau")
async def get_nb_inscriptions_zone_benevoles_route(festival_id: int, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await get_nb_inscriptions_zone_benevole(user.user_id, festival_id)


@inscription_router.put("/poste/auto-assign-flexibles", response_model=dict, description="Auto assign flexibles to postes")
async def auto_assign_flexibles_to_postes_route(user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    result = await auto_assign_flexibles_to_postes()
    # Get active festival
    festival = await get_active_festival()
    festival_id = festival.festival_id
    # Send a message to everyone to inform them of the changes
    result2 = await send_message_to_everyone(MessageSendEveryone(festival_id=festival_id, message="Les inscriptions pour les postes ont été mises à jour. Veuillez vérifier vos inscriptions."), user.user_id, user.username, user.roles)
    return result


@inscription_router.put("/zone-benevole/auto-assign-flexibles", response_model=dict, description="Auto assign flexibles to zones benevoles")
async def auto_assign_flexibles_to_zones_benevoles_route(user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await auto_assign_flexibles_to_zones_benevoles()


@inscription_router.post("/poste/batch-inscription", response_model=dict, description="Batch inscriptions and desinscriptions to postes")
async def batch_inscription_poste_route(batch: BatchInscriptionPoste, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await batch_inscription_poste(user,batch)
    
@inscription_router.post("/zone-benevole/batch-inscription", response_model=dict, description="Batch inscriptions and desinscriptions to zones benevoles")
async def batch_inscription_zone_benevole_route(batch: BatchInscriptionZoneBenevole, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await batch_inscription_zone_benevole(user,batch)

@inscription_router.post("/poste/details", response_model=list, description="Get inscriptions for a poste")
async def get_inscriptions_poste_route(poste: InscriptionPoste, user: Annotated[User, Security(verify_token, scopes=["Referent"])]):
    return await get_inscriptions_poste(poste)

@inscription_router.post("/zone-benevole/details", response_model=list, description="Get inscriptions for a zone benevole")
async def get_inscriptions_zone_benevole_route(zone_benevole: InscriptionZoneBenevole, user: Annotated[User, Security(verify_token, scopes=["Referent"])]):
    return await get_inscriptions_zone_benevole(zone_benevole)

@inscription_router.put("/poste/assign", response_model=dict, description="Assign a user to a poste")
async def assign_user_to_poste_route(poste: AssignInscriptionPoste, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    result = await assign_user_to_poste(poste)
    message = f"{user.username} vous a assigné au poste {poste.poste} pour le {poste.jour} à {poste.creneau}."
    result2 = await send_message(MessageSend(festival_id=poste.festival_id, message=message, user_to=poste.user_id), user.user_id, user.username, user.roles)
    return result
    

@inscription_router.delete("/poste/assign", response_model=dict, description="Delete a user's inscription to a poste")
async def delete_user_to_poste_route(poste: AssignInscriptionPoste, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await delete_user_to_poste(poste)

@inscription_router.delete("/zone-benevole/assign", response_model=dict, description="Delete a user's inscription to a zone benevole")
async def delete_user_to_zone_benevole_route(zone_benevole: AssignInscriptionZoneBenevole, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await delete_user_to_zone_benevole(zone_benevole)

@inscription_router.post("/poste/flexibles", response_model=list, description="Get flexibles with regards to a jour or a creneau")
async def get_flexibles_poste_route(query: FlexiblesQuery, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await get_flexibles(query.festival_id, query.jour, query.creneau)

# @inscription_router.get("/poste/my-postes", response_model=list, description="Get my postes inscriptions")
# async def get_my_postes_inscriptions_route(user: Annotated[User, Security(verify_token, scopes=["User"])]):
#     return await get_postes_inscriptions_user(user)

# @inscription_router.get("/zone-benevole/my-zones-benevoles", response_model=list, description="Get my zones benevoles inscriptions")
# async def get_my_zones_benevoles_inscriptions_route(user: Annotated[User, Security(verify_token, scopes=["User"])]):
#     return await get_zones_benevoles_inscriptions_user(user)