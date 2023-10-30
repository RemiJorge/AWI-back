from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from typing import Annotated
from .auth import verify_token
from ..controllers.user_controller import find_user_by_username
from ..models.user import User

# fichier purement test, ne pas prendre en compte

user_router = APIRouter(
    prefix="/users",
    tags=["user"]
)

@user_router.get("/{username}", response_model=User)
async def get_data(username: str, token: Annotated[None, Security(verify_token, scopes=["Admin"])]):
    return find_user_by_username(user.username)
