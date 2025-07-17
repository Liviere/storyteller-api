import os

import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import create_tables
from app.routers.stories import router as stories_router
from app.routers.llm import router as llm_router

load_dotenv()  # Load environment variables from .env file

SENTRY_DSN = os.getenv("SENTRY_DSN")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,  # Sentry DSN from environment variable
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-collected/ for more info
        send_default_pii=True,
    )


def create_app() -> FastAPI:
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
    app.include_router(llm_router)

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
        from sqlalchemy import text

        from app.database.connection import engine

        try:
            # Test database connection
            with engine.connect() as connection:
                connection.scalar(text("SELECT 1"))
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

    return app


# Create the app instance
app = create_app()
