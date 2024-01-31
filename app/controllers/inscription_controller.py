from ..database.db_session import get_db
from fastapi import HTTPException
from ..models.user import User
from ..models.inscription import InscriptionPoste, InscriptionZoneBenevole, BatchInscriptionPoste, BatchInscriptionZoneBenevole

db = get_db()

JOURS = ["Vendredi", "Samedi", "Dimanche"]
CRENEAUX = ["8h-10h", "10h-12h", "12h-14h", "14h-16h", "16h-18h"]
INSERT_QUERY = """
    INSERT INTO inscriptions (user_id, festival_id, poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau, is_poste)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    ON CONFLICT (user_id, festival_id, poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau, is_poste) DO NOTHING;
    """
DELETE_QUERY = """
    DELETE FROM inscriptions
    WHERE user_id = $1 AND poste = $2 AND zone_plan = $3 AND zone_benevole_id = $4 AND zone_benevole_name = $5 AND jour = $6 AND creneau = $7 AND is_poste = $8 AND is_active = True;
    """
SELECT_POSTES_QUERY = """
    SELECT festival_id, poste
    FROM postes
    WHERE is_active = True;
    """
SELECT_NB_INS_POSTES_QUERY = """
    SELECT festival_id, poste, jour, creneau, COUNT(*) AS nb_inscriptions
    FROM inscriptions
    WHERE is_poste = True AND is_active = True AND CUSTOM_FILTER
    GROUP BY festival_id, poste, jour, creneau
    ORDER BY festival_id, poste, jour, creneau;
    """
NO_FILTER = """ 1 = 1 """
USER_FILTER = """ user_id = $1 """

SELECT_ZONES_BENEVOLES_QUERY = """
    SELECT DISTINCT zone_plan, zone_benevole_id, zone_benevole
    FROM csv
    WHERE a_animer = 'oui';
    """
SELECT_NB_INS_ZONES_BENEVOLES_QUERY = """
    SELECT festival_id, poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau, COUNT(*) AS nb_inscriptions
    FROM inscriptions
    WHERE is_poste = False AND is_active = True AND CUSTOM_FILTER
    GROUP BY festival_id, poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau
    ORDER BY festival_id, poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau;
    """




# Function to sign up to a "poste"
async def inscription_user_poste(user: User, inscription: InscriptionPoste):
    query = INSERT_QUERY

    result = await db.execute(query, user.user_id, inscription.festival_id, inscription.poste, "", "", "", inscription.jour, inscription.creneau, True)
    
    return {"message": "Successfully signed up to poste"}

# Function to sign up to a "zone benevole"
async def inscription_user_zone_benevole(user: User, inscription: InscriptionZoneBenevole):
    query = INSERT_QUERY

    result = await db.execute(query, user.user_id, inscription.festival_id, inscription.poste, inscription.zone_plan, inscription.zone_benevole_id, inscription.zone_benevole_name, inscription.jour, inscription.creneau, False)

    return {"message": "Successfully signed up to zone benevole"}

# Function to remove an inscription from a "poste"
async def desinscription_user_poste(user: User, inscription: InscriptionPoste):
    query = DELETE_QUERY

    result = await db.execute(query, user.user_id, inscription.poste, "", "", "", inscription.jour, inscription.creneau, True)

    return {"message": "Successfully removed inscription from poste"}

# Function to remove an inscription from a "zone benevole"
async def desinscription_user_zone_benevole(user: User, inscription: InscriptionZoneBenevole):
    query = DELETE_QUERY

    result = await db.execute(query, user.user_id, inscription.poste, inscription.zone_plan, inscription.zone_benevole_id, inscription.zone_benevole_name, inscription.jour, inscription.creneau, False)

    return {"message": "Successfully removed inscription from zone benevole"}


# Function that returns the number of inscriptions for all postes by day and creneau
async def get_nb_inscriptions_poste():
    # First get all of the possible postes
    query = SELECT_POSTES_QUERY
    
    result = await db.fetch_rows(query)
    
    to_send = []
    for jour in JOURS:
        for creneau in CRENEAUX:
            to_send += [{"festival_id": row["festival_id"], "poste": row["poste"], "jour": jour, "creneau": creneau, "nb_inscriptions": 0} for row in result]
    
    filter = NO_FILTER
    query = SELECT_NB_INS_POSTES_QUERY.replace("CUSTOM_FILTER", filter)

    result = await db.fetch_rows(query)
    
    # Update the nb_inscriptions for each poste
    for row in result:
        for poste in to_send:
            if row["poste"] == poste["poste"] and row["jour"] == poste["jour"] and row["creneau"] == poste["creneau"]:
                poste["nb_inscriptions"] = row["nb_inscriptions"]
    
    return to_send

# Function that returns the number of inscriptions for all zones benevoles by day and creneau
async def get_nb_inscriptions_zone_benevole():
    # First get all of the possible zone benevoles
    query = SELECT_ZONES_BENEVOLES_QUERY
    
    result = await db.fetch_rows(query)

    to_send = []
    for jour in JOURS:
        for creneau in CRENEAUX:
            to_send += [{"poste": "Animation", "zone_plan": row["zone_plan"], "zone_benevole_id": row["zone_benevole_id"], "zone_benevole_name": row["zone_benevole"], "jour": jour, "creneau": creneau, "nb_inscriptions": 0} for row in result]
    
    filter = NO_FILTER
    query = SELECT_NB_INS_ZONES_BENEVOLES_QUERY.replace("CUSTOM_FILTER", filter)

    result = await db.fetch_rows(query)
    
    # Update the nb_inscriptions for each zone benevole
    for row in result:
        for zone_benevole in to_send:
            if row["zone_plan"] == zone_benevole["zone_plan"] and row["zone_benevole_id"] == zone_benevole["zone_benevole_id"] and row["zone_benevole_name"] == zone_benevole["zone_benevole_name"] and row["jour"] == zone_benevole["jour"] and row["creneau"] == zone_benevole["creneau"]:
                zone_benevole["nb_inscriptions"] = row["nb_inscriptions"]
                
    return to_send


# Function to auto assign flexibles to postes
async def auto_assign_flexibles_to_postes():
    # Remove duplicates with regards to poste, jour and creneau
    # Lets say we have a flexible that is signed up to n postes for a given jour and creneau
    # We will delete n-1 of his inscriptions and keep one at random
    # For each inscription that is deleted for the poste "Animation",
    # we will also delete the inscriptions for the zone benevoles under the poste "Animation" for the same jour and creneau
    query = """
    WITH DuplicateCTE AS (
        SELECT
            user_id,
            poste,
            jour,
            creneau,
            ROW_NUMBER() OVER (PARTITION BY user_id, jour, creneau ORDER BY RANDOM()) AS row_num
        FROM
            inscriptions
        WHERE
            is_poste = True
        )
    DELETE FROM
        inscriptions
    WHERE
        ((user_id, jour, creneau, poste) IN (
            SELECT
            user_id,
            jour,
            creneau,
            poste
            FROM
                DuplicateCTE
            WHERE
                row_num > 1
        ) AND is_poste = True)
    OR
        (poste = 'Animation' AND (user_id, jour, creneau) IN (
            SELECT
            user_id,
            jour,
            creneau
            FROM
                DuplicateCTE
            WHERE
                poste = 'Animation' AND row_num > 1
        ) AND is_poste = False);
    """
    
    await db.execute(query)
    
    return {"message": "Successfully auto assigned flexibles to postes"}

# Function to auto assign flexibles to zones benevoles
async def auto_assign_flexibles_to_zones_benevoles():
    # Remove duplicates with regards to zone_plan, zone_benevole_id, zone_benevole_name, jour and creneau
    # Lets say we have a flexible that is signed up to n zone_benevoles for a given jour and creneau
    # We will delete n-1 of his inscriptions and keep one at random
    
    # We have to make sure that the flexibilities for postes are already assigned
    await auto_assign_flexibles_to_postes()
   
    query = """
    WITH DuplicateCTE AS (
        SELECT
            user_id,
            poste,
            zone_plan,
            zone_benevole_id,
            zone_benevole_name,
            jour,
            creneau,
            ROW_NUMBER() OVER (PARTITION BY user_id, jour, creneau ORDER BY RANDOM()) AS row_num
        FROM
            inscriptions
        WHERE
            is_poste = False
            AND poste = 'Animation'
        )
        DELETE FROM
        inscriptions
        WHERE
        (user_id, jour, creneau, poste, zone_plan, zone_benevole_id, zone_benevole_name) IN (
            SELECT
            user_id,
            jour,
            creneau,
            poste,
            zone_plan,
            zone_benevole_id,
            zone_benevole_name
            FROM
                DuplicateCTE
            WHERE
                row_num > 1
        ) AND is_poste = False;"""
        
    await db.execute(query)
        
    return {"message": "Successfully auto assigned flexibles to zones benevoles"}


# Function to handle batch inscription and desinscription to postes
async def batch_inscription_poste(user: User, batch_inscription: BatchInscriptionPoste):
    
    if len(batch_inscription.desinscriptions) > 0:
        # Desinscriptions
        desincriptions = batch_inscription.desinscriptions
        
        # Make a list of tuples of the desincriptions
        desincriptions = [(user.user_id, inscription.poste, "", "", "", inscription.jour, inscription.creneau, True) for inscription in desincriptions]
        
        query = DELETE_QUERY
        
        await db.execute_many(query, desincriptions)
        
    if len(batch_inscription.inscriptions) > 0:
        # Inscriptions
        inscriptions = batch_inscription.inscriptions
        
        # Make a list of tuples of the inscriptions
        inscriptions = [(user.user_id, inscription.festival_id, inscription.poste, "", "", "", inscription.jour, inscription.creneau, True) for inscription in inscriptions]
        
        query = INSERT_QUERY
        
        await db.execute_many(query, inscriptions)
    
    return {"message": "Successfully handled batch inscriptions and desinscriptions to postes"}


# Function to handle batch inscription and desinscription to zones benevoles
async def batch_inscription_zone_benevole(user: User, batch_inscription: BatchInscriptionZoneBenevole):
    
    if len(batch_inscription.desinscriptions) > 0:
        # Desinscriptions
        desincriptions = batch_inscription.desinscriptions
        
        # Make a list of tuples of the desincriptions
        desincriptions = [(user.user_id, inscription.poste, inscription.zone_plan, inscription.zone_benevole_id, inscription.zone_benevole_name, inscription.jour, inscription.creneau, False) for inscription in desincriptions]
        
        query = DELETE_QUERY
        
        await db.execute_many(query, desincriptions)
        
    if len(batch_inscription.inscriptions) > 0:
        # Inscriptions
        inscriptions = batch_inscription.inscriptions
        
        # Make a list of tuples of the inscriptions
        inscriptions = [(user.user_id, inscription.festival_id, inscription.poste, inscription.zone_plan, inscription.zone_benevole_id, inscription.zone_benevole_name, inscription.jour, inscription.creneau, False) for inscription in inscriptions]
        
        query = INSERT_QUERY
        
        await db.execute_many(query, inscriptions)
    
    return {"message": "Successfully handled batch inscriptions and desinscriptions to zones benevoles"}

# Function to get the postes inscriptions of a user
async def get_postes_inscriptions_user(user: User):
    # First get all of the possible postes
    query = SELECT_POSTES_QUERY
    
    result = await db.fetch_rows(query)
    
    to_send = []
    for jour in JOURS:
        for creneau in CRENEAUX:
            to_send += [{"festival_id": row["festival_id"], "poste": row["poste"], "jour": jour, "creneau": creneau, "nb_inscriptions": 0} for row in result]
    
    filter = USER_FILTER
    query = SELECT_NB_INS_POSTES_QUERY.replace("CUSTOM_FILTER", filter)

    result = await db.fetch_rows(query, user.user_id)
    
    # Update the nb_inscriptions for each poste
    for row in result:
        for poste in to_send:
            if row["poste"] == poste["poste"] and row["jour"] == poste["jour"] and row["creneau"] == poste["creneau"]:
                poste["nb_inscriptions"] = row["nb_inscriptions"]
    
    return to_send


# Function to get the zones benevoles inscriptions of a user
async def get_zones_benevoles_inscriptions_user(user: User):
    # First get all of the possible zone benevoles
    query = SELECT_ZONES_BENEVOLES_QUERY
    
    result = await db.fetch_rows(query)

    to_send = []
    for jour in JOURS:
        for creneau in CRENEAUX:
            to_send += [{"poste": "Animation", "zone_plan": row["zone_plan"], "zone_benevole_id": row["zone_benevole_id"], "zone_benevole_name": row["zone_benevole"], "jour": jour, "creneau": creneau, "nb_inscriptions": 0} for row in result]
    
    filter = USER_FILTER
    query = SELECT_NB_INS_ZONES_BENEVOLES_QUERY.replace("CUSTOM_FILTER", filter)

    result = await db.fetch_rows(query, user.user_id)
    
    # Update the nb_inscriptions for each zone benevole
    for row in result:
        for zone_benevole in to_send:
            if row["zone_plan"] == zone_benevole["zone_plan"] and row["zone_benevole_id"] == zone_benevole["zone_benevole_id"] and row["zone_benevole_name"] == zone_benevole["zone_benevole_name"] and row["jour"] == zone_benevole["jour"] and row["creneau"] == zone_benevole["creneau"]:
                zone_benevole["nb_inscriptions"] = row["nb_inscriptions"]
                
    return to_send