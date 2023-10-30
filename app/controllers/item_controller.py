from typing import List
from fastapi import HTTPException, status
from ..database.db_session import get_db
from ..models.item import Item  

db = get_db()

# Custom exception
class RecordNotFound(Exception):
    def __init__(self, message="Record not found"):
        self.message = message
        super().__init__(self.message)


# Function to create a new item
async def create_item(item: Item) -> Item:
    query = "INSERT INTO items (name, description) VALUES ($1, $2) RETURNING item_id;"
    try:
        result = await db.fetch_val(query, item.name, item.description)
        item.item_id = result
        return item
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create the item. Please try again later. " + str(e),
        )

# Function to retrieve all items
async def find_all_items() -> List[Item]:
    query = "SELECT item_id, name, description FROM items"
    try: 
        result = await db.fetch_rows(query)
        return [Item(item_id=row["item_id"], name=row["name"], description=row["description"]) for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve items. Please try again later. " + str(e),
        )

# Function to retrieve a single item by ID
async def find_item_by_id(item_id: int) -> Item:
    query = "SELECT item_id, name, description FROM items WHERE item_id = $1"
    try:
        result = await db.fetch_row(query, item_id)
        if result:
            return Item(item_id=result["item_id"], name=result["name"], description=result["description"])
        raise RecordNotFound
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve item. Please try again later. " + str(e),
        )

# Function to delete an item by ID
async def delete_item(item_id: int):
    query = "DELETE FROM items WHERE item_id = $1"
    try:
        deleted_rows = await db.execute(query, item_id)
        if deleted_rows == "DELETE 1":
            return {"message": "Item deleted"}
        raise RecordNotFound
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item. Please try again later. " + str(e),
        )

# Function to delete all items
async def delete_all_items():
    query = "DELETE FROM items"
    try:
        deleted_rows = await db.execute(query)
        if deleted_rows != "DELETE 0":
            return {"message": "All items deleted"}
        raise RecordNotFound
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete items. Please try again later. " + str(e),
        )
