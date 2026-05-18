from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# We are creating local SQLite file name interview_data.db
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./interview_data.db"

# The engine is the core connection to the database
engine =create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} # Required for AQLite in async FastAPI

)

# This creates temp database sessions for each API request
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


# All our daatbase tables will inherit from this Base class
Base = declarative_base()

async def get_db():
    """
    Dependency function. Every time an API route needs the database,
    it will call this to get a fresh, safe connection, and close it when done.
    """
    async with AsyncSessionLocal() as session:
        yield session
        