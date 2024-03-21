from fastapi import APIRouter, Security
from typing import Annotated
from ..controllers.auth_controller import verify_token
from ..controllers.poste_controller import (
    create_poste,
    get_all_postes,
    delete_poste,
    get_referents_for_poste
)
from ..models.user import User
from pydantic import BaseModel


poste_router = APIRouter(
    prefix="/poste",
    tags=["poste"],
)

class CreatePoste(BaseModel):
    festival_id: int
    name: str
    description: str = ""
    max_capacity: int = 10
    
class DeletePoste(BaseModel):
    festival_id: int
    name: str

class PosteQuery(BaseModel):
    festival_id: int

# Create a poste
@poste_router.post("/", response_model=dict, description="Create a poste")
async def create_poste_route(poste: CreatePoste, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await create_poste(poste.festival_id, poste.name, poste.description, poste.max_capacity)

# Get all postes for a festival
@poste_router.get("/{festival_id}", response_model=list, description="Get all postes")
async def get_all_postes_route(festival_id: int, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await get_all_postes(festival_id)

# Delete a poste
@poste_router.delete("/", response_model=dict, description="Delete a poste")
async def delete_poste_route(poste: DeletePoste, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await delete_poste(poste.festival_id, poste.name)


# Get referents for a poste
@poste_router.get("/{festival_id}/{poste}", description="Get referents by poste")
async def get_referents_poste_route(festival_id: int, poste: str, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await get_referents_for_poste(festival_id, poste)