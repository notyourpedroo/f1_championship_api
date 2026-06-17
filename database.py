"""
Configuração de Banco de Dados para F1 Championship API.

Este módulo configura e gerencia a conexão com o banco de dados usando SQLAlchemy.
Fornece engine, session maker e dependency injection para endpoints FastAPI.

Environment Variables:
    DATABASE_URL (opcional): URL do banco de dados em formato SQLite/PostgreSQL
    
Usage:
    import database
    
    # Usar diretamente
    with database.engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM teams"))
    
    # Usar como dependency em FastAPI
    from database import get_db
    
    @app.get("/items")
    async def read_items(db: Session = Depends(get_db)):
        ...
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_PATH = os.getenv("DATABASE_URL", "sqlite:///f1_championship.db")


def get_db():
    """
    Dependency para injetar sessão de banco de dados em endpoints FastAPI.
    
    Cria uma nova sessão, a passa para o endpoint e garante fechamento adequado
    
    Yields:
        Session: Instância de SQLAlchemy Session
        
    Raises:
        Exception: Se ocorrer erro durante criação ou fechamento da sessão
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


engine = create_engine(
    DB_PATH,
    connect_args={"check_same_thread": False},
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
