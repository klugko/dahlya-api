from fastapi import APIRouter

from app.api.endpoints import users
from app.api.endpoints import cvs
from app.api.endpoints import recommendations
from app.api.endpoints import feedbacks

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Utilisateurs"])
api_router.include_router(cvs.router, prefix="/cvs", tags=["CVs"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommandations"])
api_router.include_router(feedbacks.router, prefix="/feedbacks", tags=["Retours"])
