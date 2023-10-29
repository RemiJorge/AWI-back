from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str | None = None
    name: str | None = None
    roles: list[str] = []
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str
