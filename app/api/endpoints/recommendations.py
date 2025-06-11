# app/api/endpoints/recommendations.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()

@router.get("/")
def read_recommendations(db: Session = Depends(get_db)):
    """
    Endpoint pour récupérer les recommandations (exemple).
    """
    return {"message": "Liste des recommandations (à implémenter)"}
