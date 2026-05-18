from fastapi import APIRouter
from app.api.v1.endpoints import interview
from app.api.v1.endpoints import report

api_router = APIRouter()


# Here we map the endpoints to thier specific tags and prefixes
api_router.include_router(interview.router, prefix="/interview", tags=["Interview Flow"])
api_router.include_router(report.router, prefix="/report", tags=["Report Generation"])