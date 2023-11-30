# This file contains the business logic for authentication and authorization

# Imports for authentication
from typing import Annotated

from fastapi import Depends, APIRouter, Request, Cookie
from fastapi.security import (
    OAuth2PasswordRequestForm
)
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from ..controllers.auth_controller import login_check_user_and_password, check_refresh_token_and_create_access_token, logout_remove_refresh_token

# Import models
from ..models.user import User
from ..models.auth import UserAndToken

auth_router = APIRouter(
     prefix="/auth",
     tags=["auth"]
) 

# Route to get the access token, equivalent to login
@auth_router.post("/token", response_model=UserAndToken)
async def login_for_tokens(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: JSONResponse
):
    user_and_token = await login_check_user_and_password(form_data.username, form_data.password, response)
    return user_and_token


# Route to get a new access token using the refresh token
@auth_router.post("/refresh-token", response_model=UserAndToken)
async def refresh_access_token(
    refresh_token: Annotated[str | None , Cookie()] = None
):
    payload = await check_refresh_token_and_create_access_token(refresh_token)
    return payload


# Route to revoke the refresh token
@auth_router.delete("/logout")
async def logout(
    response: JSONResponse,
    refresh_token: Annotated[str | None , Cookie()] = None
):
    message = await logout_remove_refresh_token(response, refresh_token)
    return message


# Route to register a new user in the database
# Fonction temporaire a refaire
@auth_router.post("/register")
async def register(request : Request, user: User):
    username = user.username
    email = user.email
    password = user.password
    password = get_password_hash(password)
    query = "INSERT INTO users (username, email, password) VALUES ($1, $2, $3) RETURNING user_id;"
    try:
        result = await request.app.state.db.fetch_val(query, username, email, password)
        query2 = "INSERT INTO user_roles (user_id, role_id) VALUES ($1, 2);"
        await request.app.state.db.execute(query2, result)
        return JSONResponse(content={"message": "User created successfully"}, status_code=201)
    except Exception as e:
        print(e)
        return JSONResponse(content={"message": "Error creating user"}, status_code=500)
