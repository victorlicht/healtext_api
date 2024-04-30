from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from alembic.config import Config

from models.models import Base
# Configure Alembic for database connection details

config = Config("alembic.ini")  # Replace with your Alembic config file path

# Get database URL from Alembic config
database_url = config.get_main_option("sqlalchemy.url")
# Create the SQLAlchemy engine
engine = create_engine(database_url)

# Create a declarative base for your models
Base = declarative_base()

# Create a session maker object to create database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency function to inject a database session into your FastAPI routes
def get_session():
    """
    Provides a database session object for dependency injection.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
