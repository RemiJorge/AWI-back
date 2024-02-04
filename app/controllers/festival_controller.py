from ..database.db_session import get_db
from ..models.festival import Festival

db = get_db()


# Function to create a new festival
async def create_festival(festival_name: str, festival_description: str):

    query = """
    INSERT INTO festivals (festival_name, festival_description) 
    VALUES ($1, $2)
    ON CONFLICT (festival_name) DO NOTHING
    RETURNING festival_id;"""


    result = await db.fetch_val(query, festival_name, festival_description)
    
    # Add "Animation" Poste
    query = """
    INSERT INTO postes (festival_id, poste, description_poste)
    VALUES ($1, 'Animation', 'Poste pour les animations');
    """
    
    result = await db.execute(query, result)
    

    return { "message" :"Festival created successfully" }

# Function to get all festivals
async def get_all_festivals():

    query = """
    SELECT 
        festival_id, 
        festival_name, 
        festival_description,
        is_active
    FROM festivals;"""

    result = await db.fetch_rows(query)
    
    to_send = []
    
    for row in result:
        to_send.append(Festival(festival_id=row["festival_id"], festival_name=row["festival_name"], festival_description=row["festival_description"], is_active=row["is_active"]))

    return to_send

# Function to delete a festival
async def delete_festival(festival_id: int):

    query = """
    DELETE FROM festivals 
    WHERE festival_id = $1;"""

    result = await db.execute(query, festival_id)

    return { "message" :"Festival deleted successfully" }

# Function to activate a festival
async def activate_festival(festival_id: int, is_active: bool):
    
    # Check that there is no active festival
    query = """
    SELECT
        festival_id
    FROM festivals
    WHERE is_active = TRUE;"""
    
    result = await db.fetch_row(query)
    
    if is_active == True:
        if result is not None:
            return { "message" :"There is already an active festival" }
    else:
        if result is None:
            return { "message" :"There is no active festival" }
        if result["festival_id"] != festival_id:
            return { "message" :"The festival you want to deactivate is not the active festival" }

    if is_active == False:
        # Deactivate all inscriptions
        query = """
        UPDATE inscriptions
        SET is_active = FALSE
        WHERE is_active = TRUE;"""
        
        result = await db.execute(query)
        
        # Deactivate all postes
        query = """
        UPDATE postes
        SET is_active = FALSE
        WHERE is_active = TRUE;"""
        
        result = await db.execute(query)
        
        # Deactivate all csv (zones benevoles and games)
        query = """
        UPDATE csv
        SET is_active = FALSE
        WHERE is_active = TRUE;"""
        
        result = await db.execute(query)
        
        # Deactivate all messages
        query = """
        UPDATE messages
        SET is_active = FALSE
        WHERE is_active = TRUE;"""
        
        result = await db.execute(query)
        
        # Deactivate all festivals
        query = """
        UPDATE festivals
        SET is_active = FALSE
        WHERE is_active = TRUE;"""
        
        result = await db.execute(query)
    
    if is_active == True:
        # Activate inscriptions for the festival
        query = """
        UPDATE inscriptions
        SET is_active = TRUE
        WHERE festival_id = $1;"""
        
        result = await db.execute(query, festival_id)
        
        # Activate posts for the festival
        query = """
        UPDATE postes
        SET is_active = TRUE
        WHERE festival_id = $1;"""
        
        result = await db.execute(query, festival_id)
        
        # Activate csv (zones benevoles and games) for the festival
        query = """
        UPDATE csv
        SET is_active = TRUE
        WHERE festival_id = $1;"""
    
        result = await db.execute(query, festival_id)
        
        # Activate messages for the festival
        query = """
        UPDATE messages
        SET is_active = TRUE
        WHERE festival_id = $1;"""
        
        result = await db.execute(query, festival_id)
        
        # Activate the festival
        query = """
        UPDATE festivals
        SET is_active = TRUE
        WHERE festival_id = $1;"""

        result = await db.execute(query, festival_id)

    return { "message" :"Festival activated/deactivated successfully" }


# Function to get active festival
async def get_active_festival():

    query = """
    SELECT 
        festival_id, 
        festival_name, 
        festival_description,
        is_active
    FROM festivals
    WHERE is_active = TRUE;"""

    result = await db.fetch_row(query)
    
    if result is None:
        return None
    
    return Festival(festival_id=result["festival_id"], festival_name=result["festival_name"], festival_description=result["festival_description"], is_active=result["is_active"])