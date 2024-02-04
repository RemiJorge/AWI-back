from fastapi import APIRouter, Security
from typing import Annotated, Optional
from ..controllers.auth_controller import verify_token
from ..controllers.message_controller import (
    send_message,
    get_all_messages,
    delete_message,
    delete_all_messages,
    send_message_to_everyone,
    send_message_to_poste,
    get_new_messages
)
from ..models.user import User
from ..models.message import (
    MessageSend,
    MessageSendEveryone,
    MessageSendPoste,
    Message
)

    
message_router = APIRouter(
    prefix="/message",
    tags=["message"],
)

@message_router.post("/send", response_model=dict, description="Send a message")
async def send_message_route(message: MessageSend, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await send_message(message, user.user_id, user.username, user.roles)

@message_router.get("/{festival_id}", response_model=list, description="Get all messages sent to you")
async def get_all_messages_route(festival_id: int, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await get_all_messages(festival_id, user.user_id)

@message_router.delete("", response_model=dict, description="Delete a message you sent")
async def delete_message_route(message_id: int, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await delete_message(message_id, user.user_id)

@message_router.delete("/clear-all/{festival_id}", response_model=dict, description="Delete all of the messages sent to you")
async def delete_all_messages_route(festival_id: int, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await delete_all_messages(festival_id, user.user_id)

@message_router.post("/everyone", response_model=dict, description="Send a message to everyone")
async def send_message_to_everyone_route(message: MessageSendEveryone, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await send_message_to_everyone(message, user.user_id, user.username, user.roles)

@message_router.post("/notify-poste", response_model=dict, description="Send a message to everyone in your poste")
async def send_message_to_poste_route(message: MessageSendPoste, user: Annotated[User, Security(verify_token, scopes=["Referent"])]):
    return await send_message_to_poste(message, user.user_id, user.username, user.roles)

# Get number of new messages
@message_router.get("/new/{festival_id}", response_model=dict, description="Get the number of new messages")
async def get_new_messages_route(festival_id: int, user: Annotated[User, Security(verify_token, scopes=["User"])]):
    return await get_new_messages(festival_id, user.user_id)
