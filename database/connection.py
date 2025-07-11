import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from models.story import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stories.db")

# Configure engine based on database type
if "mysql" in DATABASE_URL:
    # MySQL configuration with connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,  # Number of connections to maintain
        max_overflow=30,  # Additional connections that can be created on demand
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,  # Recycle connections every hour
        echo=False,  # Set to True for SQL query logging in development
    )
else:
    # SQLite configuration (fallback for development)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
