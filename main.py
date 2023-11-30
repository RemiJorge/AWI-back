from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
from app.database.db_session import get_db
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Create a FastAPI app
app = FastAPI(
    title="My First FastAPI",
    description="This is my first FastAPI application",
    version="0.1.0",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


@app.on_event("startup")
async def on_startup():
    try:
        db = get_db()
        await db.connect()
    except Exception as e:
        print("main ERROR while connecting: ", e)
        exit(1)
    app.state.db = db


@app.on_event("shutdown")
async def on_shutdown():
    await app.state.db.close()

# Define a root endpoint
@app.get("/")
async def read_root():
    return {"message": "Hello, World"}

# Import the routers
from app.routers.user_router import user_router
from app.routers.auth_router import auth_router
from app.routers.items_router import item_router

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(item_router)


if __name__ == "__main__":
    import uvicorn

    # Run the application using Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
