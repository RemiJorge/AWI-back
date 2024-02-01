from ..database.db_session import get_db

db = get_db()


# Function to create a new poste
async def create_poste(festival_id: int, poste: str, description_poste: str, max_capacity: int):
    
        query = """
        INSERT INTO postes (festival_id, poste, description_poste, max_capacity) 
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (festival_id, poste) DO NOTHING;"""
    
        result = await db.execute(query, festival_id, poste, description_poste, max_capacity)
    
        return { "message" :"Poste created successfully" }


# Function to get all postes for a festival
async def get_all_postes(festival_id: int):
    
        query = """
        SELECT poste_id, poste, description_poste, max_capacity
        FROM postes
        WHERE festival_id = $1;"""
    
        result = await db.fetch_rows(query, festival_id)
        
        result = [dict(row) for row in result]
    
        return result

# Function to delete a poste
async def delete_poste(festival_id: int, poste: str):
    
        query = """
        DELETE FROM postes
        WHERE festival_id = $1 AND poste = $2;"""
    
        result = await db.execute(query, festival_id, poste)
    
        return { "message" :"Poste deleted successfully" }
    