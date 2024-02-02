DROP TABLE IF EXISTS inscriptions CASCADE;
DROP TABLE IF EXISTS csv;
DROP TABLE IF EXISTS postes CASCADE;
DROP TABLE IF EXISTS festivals CASCADE;

CREATE TABLE festivals (
    festival_id SERIAL PRIMARY KEY,
    festival_name VARCHAR(255),
    festival_description VARCHAR(255),
    is_active BOOLEAN DEFAULT FALSE,
    UNIQUE (festival_name)
);

CREATE TABLE inscriptions (
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    festival_id INTEGER REFERENCES festivals(festival_id) ON DELETE CASCADE,
    poste VARCHAR(255),
    zone_plan VARCHAR(255),
    zone_benevole_id VARCHAR(255),
    zone_benevole_name VARCHAR(255),
    jour VARCHAR(255),
    creneau VARCHAR(255),
    is_poste BOOLEAN,
    is_present BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE (user_id, festival_id, poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau, is_poste)
);

CREATE TABLE csv (
    poste VARCHAR(255) DEFAULT 'Animation',
    festival_id INTEGER REFERENCES festivals(festival_id) ON DELETE CASCADE,
    jeu_id VARCHAR(255),
    nom_du_jeu VARCHAR(255),
    auteur VARCHAR(255),
    editeur VARCHAR(255),
    nb_joueurs VARCHAR(50),
    age_min VARCHAR(50),
    duree VARCHAR(50),
    type_jeu VARCHAR(50),
    notice VARCHAR(500),
    zone_plan VARCHAR(50),
    zone_benevole VARCHAR(50),
    zone_benevole_id VARCHAR(50),
    a_animer VARCHAR(3),
    recu VARCHAR(3),
    mecanismes VARCHAR(255),
    themes VARCHAR(255),
    tags VARCHAR(255),
    description TEXT,
    image_jeu VARCHAR(500),
    logo VARCHAR(500),
    video VARCHAR(255),
    from_csv BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE postes (
    festival_id INTEGER REFERENCES festivals(festival_id) ON DELETE CASCADE,
    poste_id SERIAL PRIMARY KEY,
    poste VARCHAR(255),
    description_poste TEXT,
    max_capacity INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE (festival_id, poste)
);


CREATE OR REPLACE PROCEDURE update_inscriptions_animation_zones()
LANGUAGE plpgsql
AS $$
DECLARE
    row_record record;
BEGIN
    -- Drop the temporary tables
    DROP TABLE IF EXISTS to_changeCTE;
    DROP TABLE IF EXISTS new_zones;

    -- Create the to_changeCTE
	-- These are the inscriptions in which the combination 
	-- zone_plan, zone_benevole_id, zone_benevole_name is not in the new csv table
    CREATE TEMP TABLE to_changeCTE AS
    SELECT 
        user_id,
        poste,
        zone_plan,
        zone_benevole_id,
        zone_benevole_name,
        jour,
        creneau
    FROM inscriptions
    WHERE poste = 'Animation' AND is_poste = False AND is_active = True
        AND (zone_plan, zone_benevole_id, zone_benevole_name) NOT IN (
            SELECT 
                zone_plan,
                zone_benevole_id,
                zone_benevole_name
            FROM csv
            WHERE a_animer = 'oui' AND is_active = True
        );

    -- Create the new_zones CTE
	-- Zones that will be needed for the updates
	-- There will be duplicates in the table proportionally to the number of games in each zone_plan and zone_benevole_name
    CREATE TEMP TABLE new_zones AS
    SELECT
        zone_plan,
        zone_benevole_id,
        zone_benevole,
		ROW_NUMBER() OVER(PARTITION BY zone_plan, zone_benevole_id, zone_benevole ORDER BY zone_benevole) as row_nb -- Technically not needed
    FROM csv
    WHERE zone_plan IN (SELECT zone_plan FROM to_changeCTE)
    AND a_animer = 'oui' AND is_active = True;

    -- Iterate through the to_changeCTE result set and perform updates
	-- Here we are performing an update for each row to be changed
    FOR row_record IN (SELECT * FROM to_changeCTE)
    LOOP
        UPDATE inscriptions AS i
        SET 
            zone_benevole_id = nz.zone_benevole_id,
            zone_benevole_name = nz.zone_benevole
        FROM ( -- Which row to update with
			SELECT 
				*
			FROM new_zones
			WHERE zone_plan = row_record.zone_plan -- Zone plan cannot have changed
			ORDER BY RANDOM()
			LIMIT 1
		) as nz
        WHERE -- Which row to update
            i.user_id = row_record.user_id
            AND i.jour = row_record.jour
            AND i.creneau = row_record.creneau
			AND i.zone_plan = row_record.zone_plan
			AND i.zone_benevole_id = row_record.zone_benevole_id
			AND i.zone_benevole_name = row_record.zone_benevole_name
            AND i.is_active = True;
    END LOOP;

    -- Drop the temporary tables
    DROP TABLE IF EXISTS to_changeCTE;
    DROP TABLE IF EXISTS new_zones;
END;
$$;

-- DROP TABLE IF EXISTS to_changeCTE;
-- DROP TABLE IF EXISTS new_zones;

-- CALL update_inscriptions_animation_zones();

-- SELECT * FROM inscriptions;