from ..database.db_session import get_db
from fastapi import HTTPException
from ..models.user import User
from ..models.inscription import InscriptionPoste, InscriptionZoneBenevole, BatchInscriptionPoste, BatchInscriptionZoneBenevole, AssignInscriptionPoste, AssignInscriptionZoneBenevole
import json

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
    WHERE user_id = $1 AND poste = $2 AND zone_plan = $3 AND zone_benevole_id = $4 AND zone_benevole_name = $5 AND jour = $6 AND creneau = $7 AND is_poste = $8 AND is_active = True AND festival_id = $9;
    """
DELETE_QUERY_2 = """
    DELETE FROM inscriptions
    WHERE user_id = $1 AND poste = $2 AND jour = $3 AND creneau = $4 AND is_poste = $5 AND is_active = True AND festival_id = $6;
    """
SELECT_POSTES_QUERY = """
    SELECT festival_id, poste, max_capacity
    FROM postes
    WHERE festival_id = $1;
    """
SELECT_NB_INS_POSTES_QUERY = """
    SELECT festival_id, poste, jour, creneau, COUNT(*) AS nb_inscriptions, array_agg(user_id) AS users
    FROM inscriptions
    WHERE is_poste = True AND festival_id = $1
    GROUP BY festival_id, poste, jour, creneau
    ORDER BY festival_id, poste, jour, creneau;
    """

SELECT_ZONES_BENEVOLES_QUERY = """
    SELECT DISTINCT festival_id, zone_plan, zone_benevole_id, zone_benevole
    FROM csv
    WHERE a_animer = 'oui'
    AND festival_id = $1;
    """
SELECT_NB_INS_ZONES_BENEVOLES_QUERY = """
    SELECT festival_id, poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau, COUNT(*) AS nb_inscriptions, array_agg(user_id) AS users
    FROM inscriptions
    WHERE is_poste = False AND festival_id = $1
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

    result = await db.execute(query, user.user_id, inscription.poste, "", "", "", inscription.jour, inscription.creneau, True, inscription.festival_id)
    
    # Remove the inscriptions for the zone benevoles under the poste "Animation" for the same jour and creneau
    if inscription.poste == "Animation":
        query = DELETE_QUERY_2
        result = await db.execute(query, user.user_id, inscription.poste, inscription.jour, inscription.creneau, False, inscription.festival_id)

    return {"message": "Successfully removed inscription from poste"}

# Function to remove an inscription from a "zone benevole"
async def desinscription_user_zone_benevole(user: User, inscription: InscriptionZoneBenevole):
    query = DELETE_QUERY

    result = await db.execute(query, user.user_id, inscription.poste, inscription.zone_plan, inscription.zone_benevole_id, inscription.zone_benevole_name, inscription.jour, inscription.creneau, False, inscription.festival_id)

    return {"message": "Successfully removed inscription from zone benevole"}


# Function that returns the number of inscriptions for all postes by day and creneau
# It also returns whether the user is signed up to the poste or not
async def get_nb_inscriptions_poste(user_id: int, festival_id: int):
    # First get all of the possible postes
    query = SELECT_POSTES_QUERY
    
    result = await db.fetch_rows(query, festival_id)
    
    to_send = []
    for jour in JOURS:
        for creneau in CRENEAUX:
            to_send += [{"festival_id": row["festival_id"], "poste": row["poste"], "jour": jour, "creneau": creneau, "nb_inscriptions": 0, "is_register": False, "max_capacity": row["max_capacity"]} for row in result]
    
    query = SELECT_NB_INS_POSTES_QUERY

    result = await db.fetch_rows(query, festival_id)
    
    # Update the nb_inscriptions for each poste
    for row in result:
        for poste in to_send:
            if row["poste"] == poste["poste"] and row["jour"] == poste["jour"] and row["creneau"] == poste["creneau"]:
                poste["nb_inscriptions"] = row["nb_inscriptions"]
                # Check if the user is signed up to the poste
                if user_id in row["users"]:
                    poste["is_register"] = True
    
    return to_send

# Function that returns the number of inscriptions for all zones benevoles by day and creneau
# It also returns whether the user is signed up to the zone benevole or not
async def get_nb_inscriptions_zone_benevole(user_id: int, festival_id: int):
    # First get all of the possible zone benevoles
    query = SELECT_ZONES_BENEVOLES_QUERY
    
    result = await db.fetch_rows(query, festival_id)
    
    max_capacity_dict = {}
    # Calculate the max capacity for each zone benevole
    for row in result:
        # Check if it is None
        if (row["zone_plan"], row["zone_benevole_id"], row["zone_benevole"]) not in max_capacity_dict:
            max_capacity_dict[(row["zone_plan"], row["zone_benevole_id"], row["zone_benevole"])] = 2
        elif max_capacity_dict[(row["zone_plan"], row["zone_benevole_id"], row["zone_benevole"])] < row["nb_inscriptions"]:
            max_capacity_dict[(row["zone_plan"], row["zone_benevole_id"], row["zone_benevole"])] = row["nb_inscriptions"]

    to_send = []
    for jour in JOURS:
        for creneau in CRENEAUX:
            to_send += [{"festival_id": row["festival_id"], "poste": "Animation", "zone_plan": row["zone_plan"], "zone_benevole_id": row["zone_benevole_id"], "zone_benevole_name": row["zone_benevole"], "jour": jour, "creneau": creneau, "nb_inscriptions": 0, "is_register": False, "max_capacity": max_capacity_dict[(row["zone_plan"], row["zone_benevole_id"], row["zone_benevole"])]} for row in result]
    
    query = SELECT_NB_INS_ZONES_BENEVOLES_QUERY

    result = await db.fetch_rows(query, festival_id)
    
    
    # Update the nb_inscriptions for each zone benevole
    for row in result:
        for zone_benevole in to_send:
            if row["zone_plan"] == zone_benevole["zone_plan"] and row["zone_benevole_id"] == zone_benevole["zone_benevole_id"] and row["zone_benevole_name"] == zone_benevole["zone_benevole_name"] and row["jour"] == zone_benevole["jour"] and row["creneau"] == zone_benevole["creneau"]:
                zone_benevole["nb_inscriptions"] = row["nb_inscriptions"]
                # Check if the user is signed up to the zone benevole
                if user_id in row["users"]:
                    zone_benevole["is_register"] = True
                
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
            AND is_active = True
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
        ) AND is_poste = True AND is_active = True)
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
        ) AND is_poste = False AND is_active = True);
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
            AND is_active = True
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
        ) AND is_poste = False AND is_active = True;"""
        
    await db.execute(query)
        
    return {"message": "Successfully auto assigned flexibles to zones benevoles"}


# Function to handle batch inscription and desinscription to postes
async def batch_inscription_poste(user: User, batch_inscription: BatchInscriptionPoste):
    
    if len(batch_inscription.desinscriptions) > 0:
        # Desinscriptions
        desincriptions = batch_inscription.desinscriptions
        
        # Make a list of tuples of the desincriptions
        desincriptions = [(user.user_id, inscription.poste, "", "", "", inscription.jour, inscription.creneau, True, inscription.festival_id) for inscription in desincriptions]
        
        query = DELETE_QUERY
        
        await db.execute_many(query, desincriptions)
        
        desincriptions = batch_inscription.desinscriptions
        
        desincriptions_zone = []
        
        # Remove the inscriptions for the zone benevoles under the poste "Animation" for the same jour and creneau
        for inscription in desincriptions:
            if inscription.poste == "Animation":
                desincriptions_zone.append((user.user_id, inscription.poste, inscription.jour, inscription.creneau, False, inscription.festival_id))
                
        if len(desincriptions_zone) > 0:
            query = DELETE_QUERY_2      
            await db.execute_many(query, desincriptions_zone)
                
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
        desincriptions = [(user.user_id, inscription.poste, inscription.zone_plan, inscription.zone_benevole_id, inscription.zone_benevole_name, inscription.jour, inscription.creneau, False, inscription.festival_id) for inscription in desincriptions]
        
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


# Function to get the inscriptions for a poste
async def get_inscriptions_poste(poste: InscriptionPoste):
    query = """
        SELECT
            users.user_id,
            users.username,
            CASE
                WHEN (
                    SELECT COUNT(*)
                    FROM inscriptions
                    WHERE user_id = users.user_id
                        AND jour = $2
                        AND creneau = $3
                        AND is_poste = True
                        AND festival_id = $4
                    GROUP BY user_id
                ) > 1 THEN True
                ELSE False
            END AS is_flexible
        FROM
            inscriptions
        INNER JOIN
            users ON users.user_id = inscriptions.user_id
        WHERE
            poste = $1
            AND jour = $2
            AND creneau = $3
            AND is_poste = True
            AND festival_id = $4;
    """
    
    result = await db.fetch_rows(query, poste.poste, poste.jour, poste.creneau, poste.festival_id)
    
    result = [dict(row) for row in result]
    
    return result


# Function to get the inscriptions for a zone benevole
async def get_inscriptions_zone_benevole(zone_benevole: InscriptionZoneBenevole):
    query = """
        SELECT
            users.user_id,
            users.username
        FROM
            inscriptions
        INNER JOIN
            users ON users.user_id = inscriptions.user_id
        WHERE
            poste = $1
            AND zone_plan = $2
            AND zone_benevole_id = $3
            AND zone_benevole_name = $4
            AND jour = $5
            AND creneau = $6
            AND is_poste = False
            AND festival_id = $7;
    """
    
    result = await db.fetch_rows(query, zone_benevole.poste, zone_benevole.zone_plan, zone_benevole.zone_benevole_id, zone_benevole.zone_benevole_name, zone_benevole.jour, zone_benevole.creneau, zone_benevole.festival_id)
    
    result = [dict(row) for row in result]
    
    return result



# Function to assign an inscription to a user
# Delete all OTHER inscriptions for the user for that jour and creneau
async def assign_user_to_poste(poste: AssignInscriptionPoste):
    query = """
        DELETE FROM
            inscriptions
        WHERE
            poste != $1
            AND jour = $2
            AND creneau = $3
            AND festival_id = $4
            AND user_id = $5;
    """
    
    await db.execute(query, poste.poste, poste.jour, poste.creneau, poste.festival_id, poste.user_id)
    
    return {"message": "Successfully assigned user to poste"}


# Function to delete an inscription to a user to a poste
async def delete_user_to_poste(poste: AssignInscriptionPoste):
    query = """
        DELETE FROM
            inscriptions
        WHERE
            poste = $1
            AND jour = $2
            AND creneau = $3
            AND is_poste = True
            AND festival_id = $4
            AND user_id = $5;
    """
    
    await db.execute(query, poste.poste, poste.jour, poste.creneau, poste.festival_id, poste.user_id)
    
    # Remove the inscriptions for the zone benevoles under the poste "Animation" for the same jour and creneau
    if poste.poste == "Animation":
        query = """
        DELETE FROM
            inscriptions
        WHERE
            poste = $1
            AND jour = $2
            AND creneau = $3
            AND is_poste = False
            AND festival_id = $4
            AND user_id = $5;
        """
        
        await db.execute(query, poste.poste, poste.jour, poste.creneau, poste.festival_id, poste.user_id)
    
    return {"message": "Successfully deleted user to poste"}


# Function to delete an inscription to a user to a zone benevole
async def delete_user_to_zone_benevole(zone_benevole: AssignInscriptionZoneBenevole):
    query = """
        DELETE FROM
            inscriptions
        WHERE
            poste = $1
            AND zone_plan = $2
            AND zone_benevole_id = $3
            AND zone_benevole_name = $4
            AND jour = $5
            AND creneau = $6
            AND is_poste = False
            AND festival_id = $7
            AND user_id = $8;
    """
    
    await db.execute(query, zone_benevole.poste, zone_benevole.zone_plan, zone_benevole.zone_benevole_id, zone_benevole.zone_benevole_name, zone_benevole.jour, zone_benevole.creneau, zone_benevole.festival_id, zone_benevole.user_id)
    
    return {"message": "Successfully deleted user to zone benevole"}


# Function to get the flexibles with regards to a jour or a creneau
async def get_flexibles(festival_id: int, jour: str, creneau: str):
    query = """
        WITH InscriptionWithRowNum AS (
            SELECT
                user_id,
                poste,
                jour,
                creneau,
                COUNT(*) OVER (PARTITION BY user_id, jour, creneau ORDER BY user_id, jour, creneau) AS partition_num
            FROM
                inscriptions
            WHERE
                is_poste = True
                AND festival_id = $1
                AND JOUR_FILTER
                AND CRENEAU_FILTER
        )
        SELECT
            u.user_id,
            u.username,
            jsonb_agg(
                jsonb_build_object(
                    'poste', i.poste,
                    'creneau', i.creneau,
                    'jour', i.jour
                )
            ) AS inscriptions
        FROM
            InscriptionWithRowNum i
        JOIN
            users u ON u.user_id = i.user_id
		WHERE
			i.partition_num > 1 
        GROUP BY
            u.user_id, u.username;
        """
        
    JOUR_FILTER = "jour = $2"
    CRENEAU_FILTER = "creneau = $3"
    
    if jour == "" or creneau == "":
        JOUR_FILTER = "1 = 1"
        CRENEAU_FILTER = "1 = 1"
        
    query = query.replace("JOUR_FILTER", JOUR_FILTER)
    query = query.replace("CRENEAU_FILTER", CRENEAU_FILTER)
    
    if jour == "" or creneau == "":
        result = await db.fetch_rows(query, festival_id)
    else:
        result = await db.fetch_rows(query, festival_id, jour, creneau)
    
    result = [dict(row) for row in result]
    
    for row in result:
        row["inscriptions"] = json.loads(row["inscriptions"])
    
    return result




# # Function to get the postes inscriptions of a user
# async def get_postes_inscriptions_user(user: User):
#     # First get all of the possible postes
#     query = SELECT_POSTES_QUERY
    
#     result = await db.fetch_rows(query)
    
#     to_send = []
#     for jour in JOURS:
#         for creneau in CRENEAUX:
#             to_send += [{"festival_id": row["festival_id"], "poste": row["poste"], "jour": jour, "creneau": creneau, "nb_inscriptions": 0} for row in result]
    
#     filter = USER_FILTER
#     query = SELECT_NB_INS_POSTES_QUERY.replace("CUSTOM_FILTER", filter)

#     result = await db.fetch_rows(query, user.user_id)
    
#     # Update the nb_inscriptions for each poste
#     for row in result:
#         for poste in to_send:
#             if row["poste"] == poste["poste"] and row["jour"] == poste["jour"] and row["creneau"] == poste["creneau"]:
#                 poste["nb_inscriptions"] = row["nb_inscriptions"]
    
#     return to_send


# # Function to get the zones benevoles inscriptions of a user
# async def get_zones_benevoles_inscriptions_user(user: User):
#     # First get all of the possible zone benevoles
#     query = SELECT_ZONES_BENEVOLES_QUERY
    
#     result = await db.fetch_rows(query)

#     to_send = []
#     for jour in JOURS:
#         for creneau in CRENEAUX:
#             to_send += [{"poste": "Animation", "zone_plan": row["zone_plan"], "zone_benevole_id": row["zone_benevole_id"], "zone_benevole_name": row["zone_benevole"], "jour": jour, "creneau": creneau, "nb_inscriptions": 0} for row in result]
    
#     filter = USER_FILTER
#     query = SELECT_NB_INS_ZONES_BENEVOLES_QUERY.replace("CUSTOM_FILTER", filter)

#     result = await db.fetch_rows(query, user.user_id)
    
#     # Update the nb_inscriptions for each zone benevole
#     for row in result:
#         for zone_benevole in to_send:
#             if row["zone_plan"] == zone_benevole["zone_plan"] and row["zone_benevole_id"] == zone_benevole["zone_benevole_id"] and row["zone_benevole_name"] == zone_benevole["zone_benevole_name"] and row["jour"] == zone_benevole["jour"] and row["creneau"] == zone_benevole["creneau"]:
#                 zone_benevole["nb_inscriptions"] = row["nb_inscriptions"]
                
#     return to_send