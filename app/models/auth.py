from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class UserAndToken(BaseModel):
    username: str
    roles: list[str]
    access_token : str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []
