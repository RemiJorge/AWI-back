from fastapi import APIRouter, Depends, Security
from typing import Annotated
from ..controllers.auth_controller import verify_token
from ..controllers.file_controller import refresh_csv_table, get_games_info, get_games_info_by_id
from ..models.user import User
from ..models.file import Game
from fastapi import File, UploadFile
import io
import csv
from pydantic import BaseModel


file_router = APIRouter(
    prefix="/file",
    tags=["file"],
)

class JeuxID(BaseModel):
    festival_id: int
    game_id: int


@file_router.post("", response_model=dict, description="Upload new csv")
async def upload_csv_route(user: Annotated[User, Security(verify_token, scopes=["Admin"])], file: UploadFile = File(...)):
    # Read the CSV file
    contents = await file.read()
    decoded_contents = contents.decode("utf-8")
    # csv_data = list(csv.DictReader(io.StringIO(decoded_contents), delimiter=";"))
    csv_data = list(csv.reader(io.StringIO(decoded_contents), delimiter=";"))

    # Exclude the header row
    csv_data = csv_data[1:]

    _ = await refresh_csv_table(csv_data)
    
    return {"message": "csv uploaded"}


@file_router.get("/jeux", response_model=list[dict], description="Get all jeux")
async def get_games_info_route(user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await get_games_info()

# Get jeux par id et par festival
@file_router.post("/jeux", response_model=dict, description="Get jeux by id and festival")
async def get_games_info_by_id_route(user: Annotated[User, Security(verify_token, scopes=["User"])], jeux_id: JeuxID):
    return await get_games_info_by_id(jeux_id.festival_id, str(jeux_id.game_id))

