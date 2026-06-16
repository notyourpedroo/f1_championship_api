import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_PATH = os.getenv("DATABASE_URL", "sqlite:///f1_championship.db")

# SQLite specific: check_same_thread=False is needed for multi-threaded apps like FastAPI
# Using QueuePool for connection pooling
engine = create_engine(
    DB_PATH,
    connect_args={"check_same_thread": False},
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
