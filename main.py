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

app.include_router(user_router)
app.include_router(auth_router)
#app.include_router(item_router)
app.include_router(file_router)
app.include_router(inscription_router)


async def insert_test_data(db):
    query = """
    DELETE FROM inscriptions WHERE user_id = 4;"""
    
    await db.execute(query)
    
    query = """
    DELETE FROM postes;"""
    
    await db.execute(query)
    
    query = """
    INSERT INTO postes (poste, description_poste, max_capacity)
    VALUES ($1, $2, $3);
    """
    
    await db.execute(query, "PosteTest1", "Description du poste 1", 2)
    await db.execute(query, "PosteTest2", "Description du poste 2", 2)
    await db.execute(query, "PosteTest3", "Description du poste 3", 2)
    await db.execute(query, "Animation", "Description du poste Animation", 2)
    
    query = """
    INSERT INTO inscriptions (user_id, poste, zone_plan, zone_benevole_id, zone_benevole_name, jour, creneau, is_poste)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8);
    """

    # Postes
    await db.execute(query, 4, "PosteTest1", "", "", "", "Lundi", "10h-12h", True)
    await db.execute(query, 4, "PosteTest2", "", "", "", "Lundi", "10h-12h", True)
    await db.execute(query, 4, "PosteTest3", "", "", "", "Lundi", "10h-12h", True)
    await db.execute(query, 4, "Animation", "", "", "", "Lundi", "10h-12h", True)
    await db.execute(query, 4, "PosteTest1", "", "", "", "Lundi", "12h-14h", True)
    await db.execute(query, 4, "PosteTest2", "", "", "", "Lundi", "12h-14h", True)
    await db.execute(query, 4, "PosteTest3", "", "", "", "Lundi", "12h-14h", True)
    await db.execute(query, 4, "Animation", "", "", "", "Lundi", "12h-14h", True)

    
    # Zones benevoles
    await db.execute(query, 4, "Animation", "ZoneTest1", "1", "ZoneTest1a", "Lundi", "10h-12h", False)
    await db.execute(query, 4, "Animation", "ZoneTest1", "2", "ZoneTest1b", "Lundi", "10h-12h", False)
    await db.execute(query, 4, "Animation", "ZoneTest1", "3", "ZoneTest1c", "Lundi", "10h-12h", False)
    await db.execute(query, 4, "Animation", "ZoneTest1", "1", "ZoneTest1a", "Lundi", "12h-14h", False)
    await db.execute(query, 4, "Animation", "ZoneTest1", "2", "ZoneTest1b", "Lundi", "12h-14h", False)
    await db.execute(query, 4, "Animation", "ZoneTest1", "3", "ZoneTest1c", "Lundi", "12h-14h", False)
    await db.execute(query, 4, "Animation", "ZoneTest2", "4", "", "Lundi", "10h-12h", False)
    await db.execute(query, 4, "Animation", "ZoneTest2", "4", "", "Lundi", "12h-14h", False)
    await db.execute(query, 4, "Animation", "ZoneTest3", "5", "", "Lundi", "10h-12h", False)
    await db.execute(query, 4, "Animation", "ZoneTest3", "5", "", "Lundi", "12h-14h", False)
    
    print("Inserted test data")



if __name__ == "__main__":
    import uvicorn

    # Run the application using Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
