DROP TABLE IF EXISTS messages;

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    festival_id INTEGER REFERENCES festivals(festival_id) ON DELETE CASCADE,
    user_to INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    user_from INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    user_from_username VARCHAR(255),
    user_from_role VARCHAR(255),
    msg VARCHAR(255),
    msg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE
);
