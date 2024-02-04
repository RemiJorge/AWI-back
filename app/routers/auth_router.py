# This file contains the business logic for authentication and authorization

# Imports for authentication
from typing import Annotated

from fastapi import Depends, APIRouter, Request, Cookie, Security
from fastapi.security import (
    OAuth2PasswordRequestForm
)
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from ..controllers.auth_controller import (
    login_check_user_and_password, 
    check_refresh_token_and_create_access_token, 
    logout_remove_refresh_token, 
    register_user,
    verify_token
)
from ..controllers.user_controller import update_user_password

# Import models
from ..models.user import User, Password
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
@auth_router.post("/signup")
async def signup(user: User):
    payload = await register_user(user)
    return payload    


# Route to change the password
@auth_router.put("/change-password")
async def change_password_route(user: Annotated[User, Security(verify_token, scopes=["User"])], password: Password):
    return await update_user_password(user.user_id, password.password)


# # Route to send an email to the user to reset the password
# @auth_router.post("/forgot-password")
# async def forgot_password(email: str):
#     subject = "Reset ton mot de passe"
#     body = "This is the body of the email. You can put your message here."

#     to_email = email
#     smtp_server = "smtp.gmail.com"
#     smtp_port = 587  # Gmail's SMTP port for TLS
#     sender_email = "festivaldujeumtp@gmail.com"
#     sender_password = "alex_remi_awi123"

#     send_email(subject, body, to_email, smtp_server, smtp_port, sender_email, sender_password)

#     return {"message": "Password reset email sent"}