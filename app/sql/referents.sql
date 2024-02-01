DROP TABLE IF EXISTS referents;

CREATE TABLE referents (
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    poste_id INT REFERENCES postes(poste_id) ON DELETE CASCADE,
    festival_id INT REFERENCES festivals(festival_id) ON DELETE CASCADE,
    UNIQUE (user_id, poste_id, festival_id)
)