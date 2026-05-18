from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine, Base

# Make sure to import your models so SQLAlchemy knows they exist!
from app.db.models import interview

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts up: creates the DP tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # We could put shutdown logic here later if needed 

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Enterprise-grade AI Interview Analyzer Backend",
        lifespan=lifespan # Added the lifespan event here!
    )

    # Attach all our modular API routes
    app.include_router(api_router,prefix=settings.API_V1_STR)

    return app

app = create_app()

@app.get("/")
async def root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME} API. Go to /docs for Swagger UI."}