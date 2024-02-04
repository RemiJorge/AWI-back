from ..database.db_session import get_db
import json
from .user_controller import get_role_ids

db = get_db()


# Function to assign a referent to a poste
async def assign_referent_to_poste(user_id: int, poste_id: int, festival_id: int):

    query = """
    INSERT INTO referents (user_id, poste_id, festival_id) 
    VALUES ($1, $2, $3)
    ON CONFLICT (user_id, poste_id, festival_id) DO NOTHING;"""

    result = await db.execute(query, user_id, poste_id, festival_id)
    
    role_ids = await get_role_ids(["Referent"])
    ref_role_id = role_ids[0]
    
    # Check if the user has the referent role
    query = """
    SELECT * FROM user_roles WHERE user_id = $1 AND role_id = $2;
    """
    
    result = await db.fetch_rows(query, user_id, ref_role_id)
    
    if len(result) == 0:
        # Insert into role table
        query = """
        INSERT INTO user_roles (user_id, role_id)
        VALUES ($1, $2);
        """
        
        result = await db.execute(query, user_id, ref_role_id)

    return { "message" :"Referent assigned to poste successfully" }

# Function to unassign a referent from a poste
async def unassign_referent_from_poste(user_id: int, poste_id: int, festival_id: int):

    query = """
    DELETE FROM referents WHERE user_id = $1 AND poste_id = $2 AND festival_id = $3;"""

    result = await db.execute(query, user_id, poste_id, festival_id)
    
    # If the user has no more postes, remove the referent role
    query = """
    SELECT * FROM referents WHERE user_id = $1;
    """
    
    result = await db.fetch_rows(query, user_id)
    
    if len(result) == 0:
        role_ids = await get_role_ids(["Referent"])
        ref_role_id = role_ids[0]
        
        query = """
        DELETE FROM user_roles WHERE user_id = $1 AND role_id = $2;
        """
        
        result = await db.execute(query, user_id, ref_role_id)

    return { "message" :"Referent unassigned from poste successfully" }

# Function to get all referents for a poste
async def get_referents_for_poste(poste_id: int, festival_id: int):

    query = """
    SELECT
        users.user_id,
        users.username,
        users.email
    FROM users
    INNER JOIN referents ON users.user_id = referents.user_id
    WHERE referents.poste_id = $1
    AND referents.festival_id = $2;"""

    result = await db.fetch_rows(query, poste_id, festival_id)
    
    result = [dict(row) for row in result]

    return result

# Function to get all users for a referent by poste
async def get_users_for_referent(user_id: int, festival_id: int):

    query = """
        SELECT
        postes.poste_id,
        inscriptions.poste,
        jsonb_agg(jsonb_build_object(
            'user_id', users.user_id,
            'username', users.username,
            'jour', inscriptions.jour,
            'creneau', inscriptions.creneau
        )) AS inscriptions
        FROM
            referents
        INNER JOIN
            postes ON referents.poste_id = postes.poste_id
        INNER JOIN
            inscriptions ON postes.poste = inscriptions.poste
        INNER JOIN
            users ON inscriptions.user_id = users.user_id
        WHERE
            referents.user_id = $1 AND inscriptions.festival_id = $2
        GROUP BY
        postes.poste_id, inscriptions.poste;
        """
    
    result = await db.fetch_rows(query, user_id, festival_id)
    
    result = [dict(row) for row in result]
    
    for row in result:
        row["inscriptions"] = json.loads(row["inscriptions"])
    
    return result
    
    
# Function to get all my postes for a referent
async def get_my_postes(user_id: int, festival_id: int):

    query = """
    SELECT
        postes.poste_id,
        postes.poste,
        postes.description_poste
    FROM
        referents
    INNER JOIN
        postes ON referents.poste_id = postes.poste_id
    WHERE
        referents.user_id = $1 AND referents.festival_id = $2;"""

    result = await db.fetch_rows(query, user_id, festival_id)
    
    result = [dict(row) for row in result]

    return result