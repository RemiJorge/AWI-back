from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db_session import get_db
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load the environment variables from the .env file
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executed on startup
    print("Startup")
    try:
        db = get_db()
        await db.connect()
    except Exception as e:
        print("main ERROR while connecting: ", e)
        exit(1)
    app.state.db = db
    await insert_test_data(db)
    yield
    # Executed on shutdown
    print("Shutdown")
    await app.state.db.close()


# Create a FastAPI app
app = FastAPI(
    title="My First FastAPI",
    description="This is my first FastAPI application",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Define a root endpoint
@app.get("/")
async def read_root():
    return {"message": "Hello, World"}

# Import the routers
from app.routers.user_router import user_router
from app.routers.auth_router import auth_router
from app.routers.items_router import item_router
from app.routers.file_router import file_router
from app.routers.inscription_router import inscription_router
from app.routers.festival_router import festival_router
from app.routers.referent_router import referent_router
from app.routers.poste_router import poste_router

app.include_router(user_router)
app.include_router(auth_router)
#app.include_router(item_router)
app.include_router(file_router)
app.include_router(inscription_router)
app.include_router(festival_router)
app.include_router(referent_router)
app.include_router(poste_router)


async def insert_test_data(db):
    # Get user_id of the test user which is user1
    query = """
    SELECT user_id FROM users WHERE username = 'user1';"""
    
    user_id = await db.fetch_val(query)
    
    # Delete test festival and create it again
    query = """
    DELETE FROM festivals WHERE festival_name = 'FestivalTest';"""
    
    await db.execute(query)
    
    query = """
    INSERT INTO festivals (festival_name, festival_description, is_active) VALUES ('FestivalTest', 'desc', True);"""
    
    await db.execute(query)
    
    # Do it again for another festival
    query = """
    DELETE FROM festivals WHERE festival_name = 'FestivalTest2';"""
    
    await db.execute(query)
    
    query = """
    INSERT INTO festivals (festival_name, festival_description) VALUES ('FestivalTest2', 'desc');"""
    
    await db.execute(query)
    
    # Select a festival
    query = """
    SELECT festival_id FROM festivals WHERE festival_name = 'FestivalTest';"""
    
    festival_id = await db.fetch_val(query)
    
    # Select another festival
    query = """
    SELECT festival_id FROM festivals WHERE festival_name = 'FestivalTest2';"""
    
    festival_id2 = await db.fetch_val(query)
    
    query = """
    DELETE FROM inscriptions WHERE user_id = $1 AND (festival_id = $2 OR festival_id = $3);"""
    
    await db.execute(query, user_id, festival_id, festival_id2)
    
    query = """
    DELETE FROM postes WHERE festival_id = $1 OR festival_id = $2;"""
    
    await db.execute(query, festival_id, festival_id2)
    
    query = """
    INSERT INTO postes (festival_id, poste, description_poste, max_capacity)
    VALUES ($1, $2, $3, $4);
    """
    
    query2 = """
    INSERT INTO postes (festival_id, poste, description_poste, max_capacity, is_active)
    VALUES ($1, $2, $3, $4, $5);
    """
    
    # For the festival FestivalTest
    await db.execute(query, festival_id, "PosteTest1", "Description du poste 1", 2)
    await db.execute(query, festival_id, "PosteTest2", "Description du poste 2", 2)
    await db.execute(query, festival_id, "PosteTest3", "Description du poste 3", 2)
    await db.execute(query, festival_id, "Animation", "Description du poste Animation", 2)
    
    # For the festival FestivalTest2
    await db.execute(query2, festival_id2, "PosteTest1", "Description du poste 1", 2, False)
    await db.execute(query2, festival_id2, "PosteTest2", "Description du poste 2", 2, False)
    await db.execute(query2, festival_id2, "PosteTest3", "Description du poste 3", 2, False)
    await db.execute(query2, festival_id2, "Animation", "Description du poste Animation", 2, False)
    
    query = """
    INSERT INTO inscriptions (user_id, festival_id, poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau, is_poste)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);
    """
    
    query2 = """
    INSERT INTO inscriptions (user_id, festival_id, poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau, is_poste, is_active)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10);
    """

    # Postes
    # Cas : Flexible sur 4 postes avec poste animation
    await db.execute(query, user_id, festival_id, "PosteTest1", "", "", "", "Samedi", "10h-12h", True)
    await db.execute(query, user_id, festival_id, "PosteTest2", "", "", "", "Samedi", "10h-12h", True)
    await db.execute(query, user_id, festival_id, "PosteTest3", "", "", "", "Samedi", "10h-12h", True)
    await db.execute(query, user_id, festival_id, "Animation", "", "", "", "Samedi", "10h-12h", True)
    await db.execute(query, user_id, festival_id, "PosteTest1", "", "", "", "Samedi", "12h-14h", True)
    await db.execute(query, user_id, festival_id, "PosteTest2", "", "", "", "Samedi", "12h-14h", True)
    await db.execute(query, user_id, festival_id, "PosteTest3", "", "", "", "Samedi", "12h-14h", True)
    await db.execute(query, user_id, festival_id, "Animation", "", "", "", "Samedi", "12h-14h", True)
    
    # For the festival FestivalTest2
    await db.execute(query2, user_id, festival_id2, "PosteTest1", "", "", "", "Vendredi", "8h-10h", True, False)
    
    # Zones benevoles
    # CONSIDER THESE TO BE DIFFERENT USERS BECAUSE YOU CAN'T BE FLEXIBLE ON ZONES BENEVOLES
    # Note : I just fixed this, disregard the above comment
    # (Might put two of the same zone benevole names when uploading new csv with renames or deletions)
    # Cas : Renommage zone benevoles et flexible
    await db.execute(query, user_id, festival_id, "Animation", "Antigone-Sud 4", "1", "ZoneTest1a", "Vendredi", "10h-12h", False)
    await db.execute(query, user_id, festival_id, "Animation", "Antigone-Sud 4", "2", "ZoneTest1b", "Samedi", "10h-12h", False)
    await db.execute(query, user_id, festival_id, "Animation", "Antigone-Sud 4", "3", "ZoneTest1c", "Dimanche", "10h-12h", False)
    await db.execute(query, user_id, festival_id, "Animation", "Antigone-Sud 4", "1", "ZoneTest1a", "Vendredi", "12h-14h", False)
    await db.execute(query, user_id, festival_id, "Animation", "Antigone-Sud 4", "2", "ZoneTest1b", "Samedi", "12h-14h", False)
    await db.execute(query, user_id, festival_id, "Animation", "Antigone-Sud 4", "3", "ZoneTest1c", "Dimanche", "12h-14h", False)
    # Cas : Tout va bien, zone plan sans zone benevole
    await db.execute(query, user_id, festival_id, "Animation", "Esplanade-Centre 4", "179", "", "Samedi", "8h-10h", False)
    await db.execute(query, user_id, festival_id, "Animation", "Esplanade-Centre 4", "179", "", "Dimanche", "8h-10h", False)
    # Cas : Tout va bien, zone plan avec zone benevole
    await db.execute(query, user_id, festival_id, "Animation", "Antigone-Nord 1", "229", "Antigone-Nord 1a", "Vendredi", "8h-10h", False)
    await db.execute(query, user_id, festival_id, "Animation", "Antigone-Nord 1", "229", "Antigone-Nord 1a", "Dimanche", "16h-18h", False)
    # Cas : Split zone plan en plusieurs zones benevoles
    await db.execute(query, user_id, festival_id, "Animation", "Esplanade-Ouest 3", "123", "", "Samedi", "14h-16h", False)
    await db.execute(query, user_id, festival_id, "Animation", "Esplanade-Ouest 3", "123", "", "Dimanche", "14h-16h", False)
    # Cas : suppression zone benevole
    await db.execute(query, user_id, festival_id, "Animation", "Antigone-Sud 4", "78", "YOOOOOOOOOOOOOOOOO", "Dimanche", "16h-18h", False)
    await db.execute(query, user_id, festival_id, "Animation", "Antigone-Sud 3", "1", "MauvaiseZoneBenevole", "Samedi", "16h-18h", False)
    
    
    # Assign a referent to a poste
    query = """
    INSERT INTO referents (user_id, poste_id, festival_id)
    VALUES ($1, $2, $3);"""
    
    # Get poste_id of the poste PosteTest1
    query2 = """
    SELECT poste_id FROM postes WHERE poste = 'PosteTest1' AND festival_id = $1;"""
    
    poste_id = await db.fetch_val(query2, festival_id)
    
    await db.execute(query, user_id, poste_id, festival_id)
    
    
    print("Inserted test data")



if __name__ == "__main__":
    import uvicorn

    # Run the application using Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
