from fastapi import APIRouter, Security
from typing import Annotated
from ..controllers.auth_controller import verify_token
from ..controllers.festival_controller import (
    create_festival,
    get_all_festivals,
    delete_festival,
    activate_festival
)
from ..models.user import User
from ..models.festival import Festival

festival_router = APIRouter(
    prefix="/festival",
    tags=["festival"],
)

@festival_router.post("", response_model=dict, description="Create a new festival")
async def create_festival_route(festival: Festival, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await create_festival(festival) 

@festival_router.get("", response_model=list[Festival], description="Get all festivals")
async def get_all_festivals_route(user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await get_all_festivals()

@festival_router.delete("", response_model=dict, description="Delete a festival")
async def delete_festival_route(festival: Festival, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await delete_festival(festival)

@festival_router.put("/activate", response_model=dict, description="Activate a festival")
async def activate_festival_route(festival: Festival, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await activate_festival(festival)

