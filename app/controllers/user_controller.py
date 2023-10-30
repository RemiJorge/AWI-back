from typing import List
from fastapi import HTTPException, status
from ..database.db_session import get_db
from ..models.user import User 

db = get_db()


# Function to get the user from the database using the username
async def find_user_by_username(username: str) -> User:
    db = get_db()
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
        username=user_dict["username"],
        email=user_dict["email"],
        name=user_dict["username"], 
        disabled=user_dict["disabled"], 
        password=user_dict["password"], 
        roles=user_dict["roles"]
        )
    return user