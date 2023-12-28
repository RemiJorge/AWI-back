from ..database.db_session import get_db
from ..models.file import Game

db = get_db()

# Function to refresh the csv table
async def refresh_csv_table(data: list):
    # Delete all the rows in the table
    query = "DELETE FROM csv;"
    await db.execute(query)

    # Insert all the rows
    columns = [
        "jeu_id", "nom_du_jeu", "auteur", "editeur",
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
    FROM csv;
    """
    
    result = await db.fetch_rows(query)
    
    result = [Game(**row) for row in result]
    
    return result


# Function to check if there are changes in the csv file regarding the:
# zone_benevole_id, zone_benevole
# It accounts for: 
# creation of new zone_benevole
# splitting of a zone_plan into multiple zone_benevole
# deletion of a zone_benevole
# renaming of a zone_benevole
async def check_and_resolve_changes():
    query= """
    CALL update_inscriptions_animation_zones();
    """
    
    await db.execute(query)
    
    return {"message": "Changes checked and resolved"}
    
