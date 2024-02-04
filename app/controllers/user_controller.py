from ..database.db_session import get_db
from ..models.user import User, UpdateUser
from passlib.context import CryptContext

# Global variables
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = get_db()

"""class User(BaseModel):
    user_id: int | None = None
    username: str
    password: str
    email: str
    telephone: str
    nom: str
    prenom: str
    tshirt: str
    vegan: bool
    hebergement: str
    association: str
    roles: list[str] = []
    disabled: bool | None = None"""

# Function to create a new user in the database
async def create_user(user: User):
    query = """
    INSERT INTO users (username, email, telephone, password, nom, prenom, tshirt, vegan, hebergement, association)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    RETURNING user_id;
    """
    user_id = await db.fetch_val(query, user.username, user.email, user.telephone, user.password, user.nom, user.prenom, user.tshirt, user.vegan, user.hebergement, user.association)
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
        u.telephone,
        u.password,
        u.disabled,
        array_agg(r.role_name) AS roles,
        u.prenom,
        u.nom,
        u.tshirt,
        u.vegan,
        u.hebergement,
        u.association
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
        telephone=user_dict["telephone"],
        name=user_dict["username"], 
        disabled=user_dict["disabled"], 
        password=user_dict["password"],
        roles=user_dict["roles"],
        prenom=user_dict["prenom"],
        nom=user_dict["nom"],
        tshirt=user_dict["tshirt"],
        vegan=user_dict["vegan"],
        hebergement=user_dict["hebergement"],
        association=user_dict["association"]
        )
    return user

# Function to get the user from the database using the email
async def find_user_by_email(email: str) -> User:
    query = """
    SELECT
        u.user_id,
        u.username,
        u.email,
        u.telephone,
        u.password,
        u.disabled,
        array_agg(r.role_name) AS roles,
        u.prenom,
        u.nom,
        u.tshirt,
        u.vegan,
        u.hebergement,
        u.association
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
        telephone=user_dict["telephone"],
        disabled=user_dict["disabled"], 
        password=user_dict["password"],
        roles=user_dict["roles"],
        prenom=user_dict["prenom"],
        nom=user_dict["nom"],
        tshirt=user_dict["tshirt"],
        vegan=user_dict["vegan"],
        hebergement=user_dict["hebergement"],
        association=user_dict["association"]
        )
    return user

# Function to get the user from the database using the user_id
async def find_user_by_user_id(user_id: int) -> User:
    query = """
    SELECT
        u.user_id,
        u.username,
        u.email,
        u.telephone,
        u.password,
        u.disabled,
        array_agg(r.role_name) AS roles,
        u.prenom,
        u.nom,
        u.tshirt,
        u.vegan,
        u.hebergement,
        u.association
    FROM
        users u
    JOIN
        user_roles ur ON u.user_id = ur.user_id
    JOIN
        roles r ON ur.role_id = r.role_id
    WHERE
        u.user_id = $1
    GROUP BY
        u.user_id, u.username, u.email;
    """
    result = await db.fetch_row(query, user_id)
    if result is None:
        return None
    user_dict = dict(result)
    user = User(
        user_id=user_dict["user_id"],
        username=user_dict["username"],
        email=user_dict["email"],
        telephone=user_dict["telephone"],
        disabled=user_dict["disabled"], 
        password="", 
        roles=user_dict["roles"],
        prenom=user_dict["prenom"],
        nom=user_dict["nom"],
        tshirt=user_dict["tshirt"],
        vegan=user_dict["vegan"],
        hebergement=user_dict["hebergement"],
        association=user_dict["association"]
        )
    return user


# Function that returns the role ids of the roles passed in parameter
async def get_role_ids(roles: list[str]) -> list[int]:
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
    
    
# Ban user by user_id
async def ban_user_by_user_id(user_id: int):
    query = """
    UPDATE users SET disabled = true WHERE user_id = $1;
    """
    await db.execute(query, user_id)
    return { "message": "User successfully banned" }


# Get all users with pagination
async def get_all_users(page: int, limit: int):
    query = """
    SELECT
        u.user_id,
        u.username,
        u.email,
        u.telephone,
        u.password,
        u.disabled,
        array_agg(r.role_name) AS roles,
        u.prenom,
        u.nom,
        u.tshirt,
        u.vegan,
        u.hebergement,
        u.association
    FROM
        users u
    JOIN
        user_roles ur ON u.user_id = ur.user_id
    JOIN
        roles r ON ur.role_id = r.role_id
    GROUP BY
        u.user_id, u.username, u.email
    ORDER BY
        u.user_id
    LIMIT $1 OFFSET $2;
    """
    offset = (page - 1) * limit
    result = await db.fetch_rows(query, limit, offset)
    users = []
    for row in result:
        user_dict = dict(row)
        user = User(
            user_id=user_dict["user_id"],
            username=user_dict["username"],
            email=user_dict["email"],
            telephone=user_dict["telephone"],
            disabled=user_dict["disabled"], 
            password="",
            roles=user_dict["roles"],
            prenom=user_dict["prenom"],
            nom=user_dict["nom"],
            tshirt=user_dict["tshirt"],
            vegan=user_dict["vegan"],
            hebergement=user_dict["hebergement"],
            association=user_dict["association"]
            )
        users.append(user)
    return users


# Function to delete all personal data
async def delete_data(user: User):
    query = """
    DELETE FROM users WHERE user_id = $1;
    """
    await db.execute(query, user.user_id)
    return { "message": "Data successfully deleted" }

# Function to update user info
async def update_user_info(user: User, new_info: UpdateUser):
    # Check if username already exists
    if new_info.username != user.username:
        user_exists = await find_user_by_username(new_info.username)
        if user_exists is not None:
            return { "message": "Username already exists" }
    # Check if email already exists
    if new_info.email != user.email:
        email_exists = await find_user_by_email(new_info.email)
        if email_exists is not None:
            return { "message": "Email already exists" }
    
    query = """
    UPDATE users
    SET
        username = $1,
        email = $2,
        telephone = $3,
        nom = $4,
        prenom = $5,
        tshirt = $6,
        vegan = $7,
        hebergement = $8,
        association = $9
    WHERE
        user_id = $10;
    """
    await db.execute(query, new_info.username, new_info.email, new_info.telephone, new_info.nom, new_info.prenom, new_info.tshirt, new_info.vegan, new_info.hebergement, new_info.association, user.user_id)
    return { "message": "User info successfully updated" }

# Function to search for users by username with pagination
async def search_users(page: int, limit: int, username: str):
    query = """
    SELECT
        u.user_id,
        u.username,
        u.email,
        u.telephone,
        u.password,
        u.disabled,
        array_agg(r.role_name) AS roles,
        u.prenom,
        u.nom,
        u.tshirt,
        u.vegan,
        u.hebergement,
        u.association
    FROM
        users u
    JOIN
        user_roles ur ON u.user_id = ur.user_id
    JOIN
        roles r ON ur.role_id = r.role_id
    WHERE
        u.username ILIKE $1
    GROUP BY
        u.user_id, u.username, u.email
    ORDER BY
        u.user_id
    LIMIT $2 OFFSET $3;
    """
    offset = (page - 1) * limit
    result = await db.fetch_rows(query, f"%{username}%", limit, offset)
    users = []
    for row in result:
        user_dict = dict(row)
        user = User(
            user_id=user_dict["user_id"],
            username=user_dict["username"],
            email=user_dict["email"],
            telephone=user_dict["telephone"],
            disabled=user_dict["disabled"], 
            password="",
            roles=user_dict["roles"],
            prenom=user_dict["prenom"],
            nom=user_dict["nom"],
            tshirt=user_dict["tshirt"],
            vegan=user_dict["vegan"],
            hebergement=user_dict["hebergement"],
            association=user_dict["association"]
            )
        users.append(user)
    return users


# Function to update user password
async def update_user_password(user_id: int, new_password: str):
    hashed_password = pwd_context.hash(new_password)
    query = """
    UPDATE users
    SET
        password = $1
    WHERE
        user_id = $2;
    """
    await db.execute(query, hashed_password, user_id)
    return { "message": "Password successfully updated" }