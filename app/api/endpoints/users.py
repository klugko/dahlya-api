
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()

@router.get("/")
def read_users(db: Session = Depends(get_db)):
    """
    Endpoint pour récupérer la liste des utilisateurs (exemple).
    """
    return {"message": "Liste des utilisateurs (à implémenter)"}
