from .db import Database

# Create a single instance of the database for the whole application
database_instance = Database()

# Function to get the database instance
def get_db():
    return database_instance

