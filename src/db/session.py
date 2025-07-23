from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings  # Import settings.py for database URI

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL  # Set up database URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()