from ..database.db_session import get_db
from ..models.festival import Festival

db = get_db()


# Function to create a new festival
async def create_festival(festival: Festival):

    query = """
    INSERT INTO festivals (festival_name, festival_description) 
    VALUES ($1, $2)
    ON CONFLICT (festival_name) DO NOTHING;"""

    result = await db.execute(query, festival.festival_name, festival.festival_description)

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
async def delete_festival(festival: Festival):

    query = """
    DELETE FROM festivals 
    WHERE festival_id = $1;"""

    result = await db.execute(query, festival.festival_id)

    return { "message" :"Festival deleted successfully" }

# Function to activate a festival
async def activate_festival(festival: Festival):

    # Deactivate all inscriptions
    query = """
    UPDATE inscriptions
    SET is_active = FALSE
    WHERE is_active = TRUE;"""
    
    result = await db.execute(query)
    
    # Activate inscriptions for the festival
    query = """
    UPDATE inscriptions
    SET is_active = TRUE
    WHERE festival_id = $1;"""
    
    result = await db.execute(query, festival.festival_id)
    
    # Deactivate all postes
    query = """
    UPDATE postes
    SET is_active = FALSE
    WHERE is_active = TRUE;"""
    
    result = await db.execute(query)
    
    # Activate posts for the festival
    query = """
    UPDATE postes
    SET is_active = TRUE
    WHERE festival_id = $1;"""
    
    result = await db.execute(query, festival.festival_id)
    
    # Deactivate all csv (zones benevoles and games)
    query = """
    UPDATE csv
    SET is_active = FALSE
    WHERE is_active = TRUE;"""
    
    result = await db.execute(query)
    
    # Activate csv (zones benevoles and games) for the festival
    query = """
    UPDATE csv
    SET is_active = TRUE
    WHERE festival_id = $1;"""
    
    result = await db.execute(query, festival.festival_id)
    
    # Deactivate all festivals
    query = """
    UPDATE festivals
    SET is_active = FALSE
    WHERE is_active = TRUE;"""
    
    result = await db.execute(query)
    
    # Activate the festival
    query = """
    UPDATE festivals
    SET is_active = TRUE
    WHERE festival_id = $1;"""

    result = await db.execute(query, festival.festival_id)

    return { "message" :"Festival activated successfully" }
