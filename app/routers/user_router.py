from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from typing import Annotated

from ..controllers.auth_controller import verify_token
from ..controllers.user_controller import find_user_by_user_id, ban_user_by_user_id, get_all_users, delete_data, update_user_info, search_users
from ..models.user import User, UpdateUser


user_router = APIRouter(
    prefix="/users",
    tags=["user"]
)

@user_router.get("/my-info", response_model=User, description="Get my info")
async def get_my_info(user: Annotated[None, Security(verify_token, scopes=["User"])]):
    return await find_user_by_user_id(user.user_id)

@user_router.get("/{user_id}", response_model=User, description="Get a user by user id")
async def get_user(user_id: int, user: Annotated[ User , Security(verify_token, scopes=["Admin"])]):
    return await find_user_by_user_id(user_id)

@user_router.put("/ban/{user_id}", response_model=dict, description="Ban a user by user id")
async def ban_user(user_id: int, user: Annotated[None, Security(verify_token, scopes=["Admin"])]):
    return await ban_user_by_user_id(user_id)

@user_router.get("/", response_model=list[User], description="Get all users")
async def get_all_users_route(user: Annotated[None, Security(verify_token, scopes=["Admin"])], page: int = 1, limit: int = 10):
    return await get_all_users(page, limit)

@user_router.delete("/delete-data", response_model=dict, description="Delete all personal data")
async def delete_data_route(user: Annotated[None, Security(verify_token, scopes=["User"])]):
    return await delete_data(user)

@user_router.put("/update-info", response_model=dict, description="Update user info")
async def update_user_info_route(user: Annotated[None, Security(verify_token, scopes=["User"])], new_info: UpdateUser):
    return await update_user_info(user, new_info)

@user_router.get("/search/username", response_model=list[User], description="Search for users by username")
async def search_users_route(user: Annotated[None, Security(verify_token, scopes=["Admin"])], username: str, page: int = 1, limit: int = 10):
    return await search_users(page, limit, username)
    

