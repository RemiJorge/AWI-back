from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
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


if __name__ == "__main__":
    import uvicorn

    # Run the application using Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
