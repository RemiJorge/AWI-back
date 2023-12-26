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
    
    # # Add the remaining rows to the csv table
    # query = """
    # SELECT poste_name
    # from postes;
    # """
    # postes = await db.fetch_rows(query)
    # postes = [poste["poste_name"] for poste in postes]
    # columns = ["poste", "from_csv"]
    # data = [[poste, False] for poste in postes]
    # await db.insert_many("csv", data, columns)
    
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
