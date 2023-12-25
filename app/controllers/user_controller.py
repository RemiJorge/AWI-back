from typing import List
from fastapi import HTTPException, status
from ..database.db_session import get_db
from ..models.user import User 

db = get_db()

# Function to create a new user in the database
async def create_user(user: User):
    query = """
    INSERT INTO users (username, email, password, disabled)
    VALUES ($1, $2, $3, $4)
    RETURNING user_id;
    """
    user_id = await db.fetch_val(query, user.username, user.email, user.password, user.disabled)
    query = """
    INSERT INTO user_roles (user_id, role_id)
    VALUES ($1, $2);
    """
    role_ids = await get_role_ids(user.roles)
    for role in role_ids:
        await db.execute(query, user_id, role)
    return { "message": "User successfully created" }


# Function to get the user from the database using the username
async def find_user_by_username(username: str) -> User:
    query = """
    SELECT
        u.user_id,
        u.username,
        u.email,
        u.password,
        u.disabled,
        array_agg(r.role_name) AS roles
    FROM
        users u
    JOIN
        user_roles ur ON u.user_id = ur.user_id
    JOIN
        roles r ON ur.role_id = r.role_id
    WHERE
        u.username = $1
    GROUP BY
        u.user_id, u.username, u.email;
    """
    result = await db.fetch_row(query, username)
    if result is None:
        return None
    user_dict = dict(result)
    user = User(
        user_id=user_dict["user_id"],
        username=user_dict["username"],
        email=user_dict["email"],
        name=user_dict["username"], 
        disabled=user_dict["disabled"], 
        password=user_dict["password"], 
        roles=user_dict["roles"]
        )
    return user

# Function to get the user from the database using the email
async def find_user_by_email(email: str) -> User:
    query = """
    SELECT
        u.user_id,
        u.username,
        u.email,
        u.password,
        u.disabled,
        array_agg(r.role_name) AS roles
    FROM
        users u
    JOIN
        user_roles ur ON u.user_id = ur.user_id
    JOIN
        roles r ON ur.role_id = r.role_id
    WHERE
        u.email = $1
    GROUP BY
        u.user_id, u.username, u.email;
    """
    result = await db.fetch_row(query, email)
    if result is None:
        return None
    user_dict = dict(result)
    user = User(
        user_id=user_dict["user_id"],
        username=user_dict["username"],
        email=user_dict["email"],
        name=user_dict["username"], 
        disabled=user_dict["disabled"], 
        password=user_dict["password"], 
        roles=user_dict["roles"]
        )
    return user


# Function that returns the role ids of the roles passed in parameter
async def get_role_ids(roles: List[str]) -> List[int]:
    roles = "(" + ", ".join([f"'{role}'" for role in roles]) + ")"
    query = f"""
    SELECT
        ARRAY_AGG(role_id) as role_ids
    FROM
        roles
    WHERE
        role_name IN {roles};
    """
    role_ids = await db.fetch_val(query)
    return role_ids
    
    
# Ban user by username
async def ban_user_by_username(username: str):
    query = """
    UPDATE users SET disabled = true WHERE username = $1;
    """
    await db.execute(query, username)
    return { "message": "User successfully banned" }