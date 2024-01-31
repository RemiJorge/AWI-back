from pydantic import BaseModel

class Festival(BaseModel):
    festival_id: int | None = None
    festival_name: str
    festival_description: str
    is_active: bool | None = None

