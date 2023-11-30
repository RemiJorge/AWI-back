DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

-- Create the "roles" table to store user roles
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(255) NOT NULL UNIQUE
);

-- Create the "users" table to store user information
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE, -- Enforce uniqueness for username
    password VARCHAR(255) NOT NULL, -- You should hash and salt the password
    email VARCHAR(255) NOT NULL UNIQUE, -- Enforce uniqueness for email
    disabled BOOLEAN DEFAULT FALSE -- Add the "disabled" column with a default value of FALSE
    -- Add other user-related fields as needed
);


-- Create the "user_roles" table to manage user-to-role relationships
CREATE TABLE user_roles (
    user_role_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    role_id INT REFERENCES roles(role_id),
    UNIQUE (user_id, role_id) -- Enforce uniqueness for the combination of user_id and role_id
);

-- Example: Insert some initial roles into the "roles" table
INSERT INTO roles (role_name) VALUES
    ('Admin'),
    ('Referent'),
    ('User'),
    ('Super');

-- Example: Insert a user into the "users" table and associate them with a role
-- Replace the password value with a hashed and salted password
INSERT INTO users (username, password, email) VALUES
    ('example_user', 'hashed_password', 'user@example.com');

-- Associate the user with a role (e.g., 'User' role)
INSERT INTO user_roles (user_id, role_id)
SELECT user_id, role_id
FROM users, roles
WHERE users.username = 'example_user' AND roles.role_name = 'User';

--Make a user have all roles
-- INSERT INTO user_roles (user_id, role_id)
-- SELECT user_id, role_id
-- FROM users, roles
-- WHERE users.username = 'example_user';

