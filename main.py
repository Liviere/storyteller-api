from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.connection import create_tables
from routers.stories import router as stories_router

app = FastAPI(
    title="Story Teller API",
    description="API for creating and managing stories",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stories_router, prefix="/api/v1", tags=["stories"])


# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()


@app.get("/")
async def root():
    return {"message": "Welcome to Story Teller API"}


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker healthcheck and monitoring"""
    from database.connection import engine
    from sqlalchemy import text
    try:
        # Test database connection
        with engine.connect() as connection:
            connection.scalar(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
