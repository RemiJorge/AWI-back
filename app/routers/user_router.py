from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from typing import Annotated

from ..controllers.auth_controller import verify_token
from ..controllers.user_controller import find_user_by_user_id, ban_user_by_user_id
from ..models.user import User


user_router = APIRouter(
    prefix="/users",
    tags=["user"]
)

@user_router.get("/{user_id}", response_model=User, description="Get a user by user id")
async def get_user(user_id: int, user: Annotated[ User , Security(verify_token, scopes=["Admin"])]):
    return await find_user_by_user_id(user_id)

@user_router.put("/ban/{user_id}", response_model=dict, description="Ban a user by user id")
async def ban_user(user_id: int, token: Annotated[None, Security(verify_token, scopes=["Admin"])]):
    return await ban_user_by_user_id(user_id)
