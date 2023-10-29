from fastapi import APIRouter, HTTPException, Depends, FastAPI, Security
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from typing import Annotated
from .auth import User, verify_token

# fichier purement test, ne pas prendre en compte

user_router = APIRouter()

@user_router.get("/get_data/{id}")
async def get_data(request : Request, id: int, user: Annotated[None, Security(verify_token, scopes=["items"])]):
    query = "SELECT * FROM users WHERE user_id = $1"
    result = await request.app.state.db.fetch_rows(query, id)
    if result is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return JSONResponse(content=[dict(row) for row in result])
