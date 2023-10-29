from typing import Optional
from pydantic import BaseModel

class Item (BaseModel):
    item_id: Optional[int] = None
    name: str
    description: str