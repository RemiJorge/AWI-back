from fastapi import APIRouter, Depends, Security
from typing import Annotated
from ..controllers.auth_controller import verify_token
from ..controllers.file_controller import refresh_csv_table, get_games_info
from ..models.user import User
from ..models.file import Game
from fastapi import File, UploadFile
import io
import csv


file_router = APIRouter(
    prefix="/file",
    tags=["file"],
)


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


@file_router.get("/jeux", response_model=list[Game], description="Get all jeux")
async def get_games_info_route(user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await get_games_info()

