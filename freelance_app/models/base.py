"""
Base SQLAlchemy configuration and database setup
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://freelance_user:freelance_pass@localhost:5432/freelance_db'
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv('SQL_ECHO', 'false').lower() == 'true',
    poolclass=NullPool if 'pytest' in os.getenv('PYTEST_CURRENT_TEST', '') else None
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


def get_db():
    """
    Database dependency for FastAPI
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)
