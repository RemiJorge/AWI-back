from pydantic import BaseModel

class MessageSend(BaseModel):
    festival_id: int
    user_to: int
    message: str
    
class MessageSendEveryone(BaseModel):
    festival_id: int
    message: str

class MessageSendPoste(BaseModel):
    festival_id: int
    poste_id: int
    message: str

class Message(BaseModel):
    message_id: int
    festival_id: int
    user_from: int
    user_to: int
    message: str