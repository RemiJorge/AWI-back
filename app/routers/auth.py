# This file contains the business logic for authentication and authorization

# Imports for authentication
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, Security, status, Request
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

# To get database session
from ..database.db_session import get_db

# GLOBAL VARIABLES

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 15


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

# Framework for authentication

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={"User": "Read information about the current user.", "Admin": "Read items."},
)

auth_router = APIRouter(
     prefix="/auth",
     tags=["auth"]
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


# This function creates the access token, it encodes the payload and signs it with the secret key
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    # Data to be encoded in the JWT
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Route to get the access token, equivalent to login
@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    # Authenticate the user (check if the user exists and the password is correct)
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # Create the access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.roles},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}



#Route to register a new user in the database
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