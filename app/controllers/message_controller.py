from ..database.db_session import get_db
from ..models.message import MessageSend, MessageSendPoste, MessageSendEveryone
from .referent_controller import get_users_for_referent

db = get_db()


# Function to send a message
async def send_message(message: MessageSend, user_id: int, username: str, roles: list):
    
    query = """
    INSERT INTO messages (festival_id, user_to, user_from, user_from_username, user_from_role, msg)
    VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING message_id;
    """
    
    role = "User"
    
    if "Referent" in roles:
        role = "Referent"
    if "Admin" in roles:
        role = "Admin"
    
    result = await db.fetch_val(query, message.festival_id, message.user_to, user_id, username, role, message.message)
    
    return {"message": "Message sent", "message_id": result}


# Function to get all messages (for yourself)
async def get_all_messages(festival_id: int, user_id: int):
        
        query = """
        SELECT * 
        FROM messages 
        WHERE user_to = $1 AND festival_id = $2;
        """
        
        result = await db.fetch_rows(query, user_id, festival_id)
        
        result = [dict(row) for row in result]
        
        # Mark all messages as read
        query = """
        UPDATE messages
        SET is_read = TRUE
        WHERE user_to = $1 AND festival_id = $2;
        """
        
        _ = await db.execute(query, user_id, festival_id)
        
        return result
    

# Function to delete a message
async def delete_message(message_id: int, user_id: int):
    
    # Check that the message was sent by the user
    query = """
    SELECT * FROM messages WHERE message_id = $1 AND user_from = $2;
    """
    
    result = await db.fetch_row(query, message_id, user_id)
    
    if not result:
        return {"message": "Message not found"}
    
    query = """
    DELETE FROM messages WHERE message_id = $1;
    """
    
    await db.execute(query, message_id)
    
    return {"message": "Message deleted"}


# Function to delete all messages
async def delete_all_messages(festival_id: int, user_id: int):
    
    query = """
    DELETE FROM messages WHERE user_to = $1 AND festival_id = $2;
    """
    
    await db.execute(query, user_id, festival_id)
    
    return {"message": "All messages deleted"}


# Function to send a message to everyone
async def send_message_to_everyone(message: MessageSendEveryone, user_id: int, username: str, roles: list):
    
    # Get all users in the festival
    query = """
    SELECT user_id FROM users;
    """
    
    result = await db.fetch_rows(query)
    
    user_ids = [row["user_id"] for row in result]
    
    role = "User"
    if "Referent" in roles:
        role = "Referent"
    if "Admin" in roles:
        role = "Admin"
    
    columns = ["festival_id", "user_to", "user_from", "user_from_username", "user_from_role", "msg"]
    
    values = [[message.festival_id, user, user_id, username, role, message.message] for user in user_ids]
    
    await db.insert_many("messages", values, columns)
    
    return {"message": "Message sent to everyone"}

# Function to send a message to a poste
async def send_message_to_poste(message: MessageSendPoste, user_id: int, username: str, roles: list):
    
    # Get all users in the poste
    result = await get_users_for_referent(user_id, message.festival_id)
    
    user_ids = []
    
    role = "User"
    if "Referent" in roles:
        role = "Referent"
    if "Admin" in roles:
        role = "Admin"
    
    for row in result:
        inscriptions = row["inscriptions"]
        for inscription in inscriptions:
            if row["poste_id"] == message.poste_id:
                if inscription["user_id"] not in user_ids:
                    user_ids.append(inscription["user_id"])
                    
    # Send the message to all users in the poste
    columns = ["festival_id", "user_to", "user_from", "user_from_username", "user_from_role", "msg"]
    
    values = [[message.festival_id, user, user_id, username, role, message.message] for user in user_ids]
    
    await db.insert_many("messages", values, columns)
    
    return {"message": "Message sent to poste"}



# Function to get the number of new messages
async def get_new_messages(festival_id: int, user_id: int):
    
    query = """
    SELECT COUNT(*) 
    FROM messages 
    WHERE user_to = $1 AND festival_id = $2 AND is_read = FALSE;
    """
    
    result = await db.fetch_val(query, user_id, festival_id)
    
    return {"new_messages": result}