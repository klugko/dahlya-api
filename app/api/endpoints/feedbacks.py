from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()

@router.get("/")
def read_feedbacks(db: Session = Depends(get_db)):
    """
    Endpoint pour récupérer les retours (exemple).
    """
    return {"message": "Liste des retours (à implémenter)"}
