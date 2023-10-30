from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str
    email: str
    name: str | None = None
    roles: list[str] = []
    disabled: bool | None = None

