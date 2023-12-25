from fastapi import APIRouter, Depends, Security
from typing import Annotated
from ..controllers.auth_controller import verify_token
from app.controllers.item_controller import (
    create_item,
    find_all_items,
    find_item_by_id,
    delete_item,
    delete_all_items,
)
from ..models.item import Item
from ..models.user import User


item_router = APIRouter(
    prefix="/items",
    tags=["item"],
)
# Note it is possible to put dependencies on the router itself
# eg: dependencies=[Security(verify_token, scopes=["Admin"])]

@item_router.post("", response_model=Item, description="Create a new item")
async def create_item_route(item: Item, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await create_item(item)

@item_router.get("", response_model=list[Item], description="Get all items")
async def get_all_items_route(user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await find_all_items()

@item_router.get("/{id}", response_model=Item, description="Get an item by ID")
async def get_item_route(id: int, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await find_item_by_id(id)

@item_router.delete("/{id}", response_model=dict, description="Delete an item by ID")
async def delete_item_route(id: int, user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await delete_item(id)

@item_router.delete("", response_model=dict, description="Delete all items")
async def delete_all_items_route(user: Annotated[User, Security(verify_token, scopes=["Admin"])]):
    return await delete_all_items()
