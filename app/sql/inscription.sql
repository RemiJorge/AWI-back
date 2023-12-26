DROP TABLE IF EXISTS inscription;
DROP TABLE IF EXISTS csv;
DROP TABLE IF EXISTS postes;

CREATE TABLE inscriptions (
    user_id INTEGER REFERENCES users(user_id),
    poste VARCHAR(255),
    zone_plan VARCHAR(255),
    zone_benevole_id VARCHAR(255),
    zone_benevole_name VARCHAR(255),
    jour VARCHAR(255),
    creneau VARCHAR(255),
    is_poste BOOLEAN
);

CREATE TABLE csv (
    poste VARCHAR(255) DEFAULT 'Animation',
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
    from_csv BOOLEAN DEFAULT TRUE
);

CREATE TABLE postes (
    poste VARCHAR(255),
    description_poste TEXT,
    max_capacity INTEGER DEFAULT 10
);
