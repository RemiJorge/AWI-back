# This file contains the business logic for authentication and authorization

# Imports for authentication
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status, Request
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from fastapi.responses import JSONResponse
import os

from ..controllers.user_controller import find_user_by_username

# Import models
from ..models.user import User
from ..models.auth import UserAndToken, TokenData


# GLOBAL VARIABLES

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 1



# Framework for authentication

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={"User": "Read information about the current user.", "Admin": "Read items."},
)

# Function to verify the password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Function to hash the password
def get_password_hash(password):
    return pwd_context.hash(password)


# Function to authenticate the user, check if the user exists and the password is correct
async def authenticate_user(username: str, password: str):
    user = await find_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


# This function creates a token, it encodes the payload and signs it with the secret key
def create_token(data: dict, expires_delta: timedelta | None = None):
    # Data to be encoded in the JWT
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



async def login_check_user_and_password(username: str, password: str, response: JSONResponse):
    # Authenticate the user (check if the user exists and the password is correct)
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # Create the access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": user.username, "scopes": user.roles},
        expires_delta=access_token_expires,
    )

    # Create refresh token
    refresh_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES * 5)
    refresh_token = create_token(
        data={"sub": user.username, "scopes": user.roles},
        expires_delta=refresh_token_expires,
    )

    # Set the cookie with the refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=refresh_token_expires.total_seconds(),
        path="/",
        samesite="None"
    )

    # Return the user and the access token
    payload = UserAndToken(username=user.username, roles=user.roles, access_token=access_token, token_type="bearer")

    return payload



async def check_refresh_token_and_create_access_token(refresh_token: str | None = None):
    try:
        # If there is no refresh token, raise an exception
        if refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        # Decode the refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    # Token expired
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # Get the user from the database
    user = await find_user_by_username(username=token_data.username)
    # If the user does not exist, raise an exception
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # Create the new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": user.username, "scopes": user.roles},
        expires_delta=access_token_expires,
    )

    # Return the user and the access token
    payload = UserAndToken(username=user.username, roles=user.roles, access_token=access_token, token_type="bearer")
    
    return payload


async def logout_remove_refresh_token(response: JSONResponse ,refresh_token: str | None = None):
    # If there is no refresh token, raise an exception
    if refresh_token is None:
        print("No refresh token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    # Set the cookie with the refresh token
    response.set_cookie(
        key="refresh_token",
        value="",
        httponly=True,
        max_age=0,
        path="/",
        samesite="None"
    )
    return {"message": "Logout successful"}



# Function that verifies the access token and the scopes
async def verify_token(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
):
    # Prepare the authentication value to be included in the response headers
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    # Prepare the exception to be raised, according to OAuth2 spec
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        # Decode the received token
        # The payload looks like this: {"sub": "johndoe", "scopes": ["me", "items"]}
        # This is in accordance with JWT standard
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        # This is to validate that the token has the required format
        token_data = TokenData(scopes=token_scopes, username=username)
    
    # Token expired
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature has expired",
            headers={"WWW-Authenticate": authenticate_value},
        )

    # Token is invalid
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Get the user from the database
    user = await find_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception

    # Check if the user is disabled
    if user.disabled:
        raise HTTPException(status_code=400, detail="Banned user")
    
    # Check if the token has the required scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )