from ..database.db_session import get_db
from fastapi import HTTPException
from ..models.user import User
from ..models.inscription import InscriptionPoste, InscriptionZoneBenevole

db = get_db()

# Function to sign up to a "poste"
async def inscription_user_poste(user: User, inscription: InscriptionPoste):
    query = """
    INSERT INTO inscriptions (user_id, poste, jour, creneau, is_poste)
    VALUES ($1, $2, $3, $4, $5)
    """

    result = await db.execute(query, user.user_id, inscription.poste, inscription.jour, inscription.creneau, True)
    
    if result != "INSERT 0 1":
        return HTTPException(status_code=500, detail="Error while signing up to poste")

    return {"message": "Successfully signed up to poste"}

# Function to sign up to a "zone benevole"
async def inscription_user_zone_benevole(user: User, inscription: InscriptionZoneBenevole):
    query = """
    INSERT INTO inscriptions (user_id, poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau, is_poste)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    """

    result = await db.execute(query, user.user_id, inscription.poste, inscription.zone_plan, inscription.zone_benevole_id, inscription.zone_benevole_name, inscription.jour, inscription.creneau, False)

    return {"message": "Successfully signed up to zone benevole"}

# Function to remove an inscription from a "poste"
async def desinscription_user_poste(user: User, inscription: InscriptionPoste):
    query = """
    DELETE FROM inscriptions
    WHERE user_id = $1 AND poste = $2 AND jour = $3 AND creneau = $4 AND is_poste = $5
    """

    result = await db.execute(query, user.user_id, inscription.poste, inscription.jour, inscription.creneau, True)

    return {"message": "Successfully removed inscription from poste"}

# Function to remove an inscription from a "zone benevole"
async def desinscription_user_zone_benevole(user: User, inscription: InscriptionZoneBenevole):
    query = """
    DELETE FROM inscriptions
    WHERE user_id = $1 AND poste = $2 AND zone_plan = $3 AND zone_benevole_id = $4 AND zone_benevole_name = $5 AND jour = $6 AND creneau = $7 AND is_poste = $8
    """

    result = await db.execute(query, user.user_id, inscription.poste, inscription.zone_plan, inscription.zone_benevole_id, inscription.zone_benevole_name, inscription.jour, inscription.creneau, False)

    return {"message": "Successfully removed inscription from zone benevole"}


# Function that returns the number of inscriptions for a given poste by day and creneau
async def get_nb_inscriptions_poste():
    query = """
    SELECT poste, jour, creneau, COUNT(*) AS nb_inscriptions
    FROM inscriptions
    WHERE is_poste = True
    GROUP BY poste, jour, creneau
    ORDER BY poste, jour, creneau
    """

    result = await db.fetch_rows(query)
    
    result = [{"poste": row["poste"], "jour": row["jour"], "creneau": row["creneau"], "nb_inscriptions": row["nb_inscriptions"]} for row in result]

    return result

# Function that returns the number of inscriptions for a given zone benevole by day and creneau
async def get_nb_inscriptions_zone_benevole():
    query = """
    SELECT poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau, COUNT(*) AS nb_inscriptions
    FROM inscriptions
    WHERE is_poste = False
    GROUP BY poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau
    ORDER BY poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau
    """

    result = await db.fetch_rows(query)
    
    result = [{"poste": row["poste"], "zone_plan": row["zone_plan"], "zone_benevole_id": row["zone_benevole_id"], "zone_benevole_name": row["zone_benevole_name"], "jour": row["jour"], "creneau": row["creneau"], "nb_inscriptions": row["nb_inscriptions"]} for row in result]

    return result