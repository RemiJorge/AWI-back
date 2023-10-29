from .db import Database

database_instance = Database()

def get_db():
    return database_instance

