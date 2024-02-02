from fastapi import APIRouter, Security
from typing import Annotated, Optional
from ..controllers.auth_controller import verify_token
from ..controllers.festival_controller import (
    create_festival,
    get_all_festivals,
    delete_festival,
    activate_festival,
    get_active_festival
)
from ..models.user import User
from ..models.festival import Festival
from pydantic import BaseModel

class CreateFestival(BaseModel):
    festival_name: str
    festival_description: str

class FestivalActivate(BaseModel):
    festival_id: int
    is_active: bool


festival_router = APIRouter(
    prefix="/festival",
    tags=["festival"],
)

@festival_router.post("", response_model=dict, description="Create a new festival")
async def create_festival_route(festival: CreateFestival, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await create_festival(festival.festival_name, festival.festival_description)

@festival_router.get("", response_model=list[Festival], description="Get all festivals")
async def get_all_festivals_route(user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await get_all_festivals()

@festival_router.delete("", response_model=dict, description="Delete a festival")
async def delete_festival_route(festival_id: int, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await delete_festival(festival_id)

@festival_router.put("/activate", response_model=dict, description="Activate a festival")
async def activate_festival_route(festival: FestivalActivate, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await activate_festival(festival.festival_id, festival.is_active)

@festival_router.get("/active", response_model=Optional[Festival], description="Get active festival")
async def get_active_festival_route(user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await get_active_festival()

