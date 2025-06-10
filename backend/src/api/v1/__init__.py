"""API v1 routes package"""

from fastapi import APIRouter

from .sql_analysis import router as sql_analysis_router
from .students import router as students_router
from .learning import router as learning_router
from .hints import router as hints_router

# Main API router for v1
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    sql_analysis_router,
    prefix="/analysis",
    tags=["SQL Analysis"]
)

api_router.include_router(
    students_router,
    prefix="/students", 
    tags=["Students"]
)

api_router.include_router(
    learning_router,
    prefix="/learning",
    tags=["Learning"]
)

api_router.include_router(
    hints_router,
    prefix="/hints",
    tags=["Hints"]
) 