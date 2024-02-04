from fastapi import APIRouter, Security
from typing import Annotated
from ..controllers.auth_controller import verify_token
from ..controllers.referent_controller import (
    assign_referent_to_poste,
    get_referents_for_poste,
    get_users_for_referent,
    unassign_referent_from_poste,
    get_my_postes
)
from ..models.user import User
from pydantic import BaseModel


referent_router = APIRouter(
    prefix="/referent",
    tags=["referent"],
)

class AssignReferent(BaseModel):
    user_id: int
    poste_id: int
    festival_id: int

class ReferentQuery(BaseModel):
    poste_id: int
    festival_id: int

@referent_router.post("/assign", response_model=dict, description="Assign a referent to a poste")
async def assign_referent_to_poste_route(poste_ref: AssignReferent, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await assign_referent_to_poste(poste_ref.user_id, poste_ref.poste_id, poste_ref.festival_id)

@referent_router.post("/", response_model=list, description="Get all referents for a poste")
async def get_referents_for_poste_route(poste: ReferentQuery, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await get_referents_for_poste(poste.poste_id, poste.festival_id)

@referent_router.get("/users/{festival_id}", response_model=list, description="Get all users for a referent by poste")
async def get_users_for_referent_route(festival_id: int,user: Annotated[User, Security(verify_token, scopes=["Referent"])]):
    return await get_users_for_referent(user.user_id, festival_id)

@referent_router.delete("/unassign", response_model=dict, description="Unassign a referent from a poste")
async def unassign_referent_from_poste_route(poste_ref: AssignReferent, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await unassign_referent_from_poste(poste_ref.user_id, poste_ref.poste_id, poste_ref.festival_id)

@referent_router.get("/my-postes/{festival_id}", response_model=list, description="Get all postes for a referent")
async def get_my_postes_route(festival_id: int, user: Annotated[User, Security(verify_token, scopes=["Referent"])]):
    return await get_my_postes(user.user_id, festival_id)