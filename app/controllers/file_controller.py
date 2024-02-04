from ..database.db_session import get_db
from ..models.file import Game

db = get_db()

# Function to refresh the csv table
async def refresh_csv_table(data: list):
    # Delete all the rows in the table
    query = "DELETE FROM csv WHERE is_active = TRUE;"
    await db.execute(query)
    
    # Get the active festival
    query = """
    SELECT festival_id FROM festivals WHERE is_active = TRUE;"""
    
    festival_id = await db.fetch_val(query)
    
    # Add the festival_id to the data
    for row in data:
        row.insert(0, festival_id)

    # Insert all the rows
    columns = [
        "festival_id", "jeu_id", "nom_du_jeu", "auteur", "editeur",
        "nb_joueurs", "age_min", "duree", "type_jeu", "notice",
        "zone_plan", "zone_benevole", "zone_benevole_id", "a_animer",
        "recu", "mecanismes", "themes", "tags", "description",
        "image_jeu", "logo", "video"
    ]

    await db.insert_many("csv", data, columns)
    
    # Call the function to check and resolve changes
    await check_and_resolve_changes()
    
    return {"message": "csv table refreshed"}

# Function to get all games
async def get_games_info() -> list[Game]:
    query = """
    SELECT * 
    FROM csv
    WHERE is_active = TRUE;
    """
    
    result = await db.fetch_rows(query)
    
    if len(result) == 0:
        return [{"message": "No games found"}]
    
    result = [Game(**row).model_dump() for row in result]
    
    return result


# Function to check if there are changes in the csv file regarding the:
# zone_benevole_id, zone_benevole
# It accounts for: 
# creation of new zone_benevole (should not have effects on inscriptions as it did not exist before)
# splitting of a zone_plan into multiple zone_benevole
# deletion of a zone_benevole
# renaming of a zone_benevole
# creating a new zone_plan (should not have effects on inscriptions as it did not exist before)

# It does NOT account for:
# renaming of a zone_plan
# deletion of a zone_plan
async def check_and_resolve_changes():
    query= """
    CALL update_inscriptions_animation_zones();
    """
    
    await db.execute(query)
    
    return {"message": "Changes checked and resolved"}


# Function to get games by id and festival
async def get_games_info_by_id(festival_id: int, game_id: str) -> Game:
    query = """
    SELECT * 
    FROM csv
    WHERE festival_id = $1 AND jeu_id = $2;
    """
    
    result = await db.fetch_row(query, festival_id, game_id)
    
    if result is None:
        return {"message": "No game found"}
    
    game = Game(**result)
    
    dict_game = game.model_dump()
    
    return dict_game
    
