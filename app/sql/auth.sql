DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- Create the "roles" table to store user roles
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(255) NOT NULL UNIQUE
);

-- Create the "users" table to store user information
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE, 
    password VARCHAR(255) NOT NULL, 
    email VARCHAR(255) NOT NULL UNIQUE,
    telephone VARCHAR(255) NOT NULL,
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    tshirt VARCHAR(255) NOT NULL,
    vegan BOOLEAN DEFAULT FALSE,
    hebergement VARCHAR(255) NOT NULL,
    association VARCHAR(255) NOT NULL, 
    disabled BOOLEAN DEFAULT FALSE 
);


-- Create the "user_roles" table to manage user-to-role relationships
CREATE TABLE user_roles (
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    role_id INT REFERENCES roles(role_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Insert some initial roles into the "roles" table
INSERT INTO roles (role_name) VALUES
    ('User'),
    ('Referent'),
    ('Admin'),
    ('Super');

-- Example: Insert a user into the "users" table and associate them with a role
-- Replace the password value with a hashed and salted password
-- INSERT INTO users (username, password, email) VALUES
--     ('example_user', 'hashed_password', 'user@example.com');

-- Associate the user with a role (e.g., 'User' role)
-- INSERT INTO user_roles (user_id, role_id)
-- SELECT user_id, role_id
-- FROM users, roles
-- WHERE users.username = 'example_user' AND roles.role_name = 'User';

--Make a user have all roles
-- INSERT INTO user_roles (user_id, role_id)
-- SELECT user_id, role_id
-- FROM users, roles
-- WHERE users.username = 'example_user';

