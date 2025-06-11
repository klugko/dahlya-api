from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine, get_db
from app.core.config import settings
from app.api.api_router import api_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="API d'Orientation Professionnelle",
    description="API pour analyser les CV et générer des recommandations professionnelles.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Inclut le routeur API principal
app.include_router(api_router)

@app.get("/")
def read_root():
    """
    Point de terminaison racine pour vérifier que l'API fonctionne.
    """
    return {"message": "Bienvenue sur l'API d'Orientation Professionnelle"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Point de terminaison de vérification de l'état de santé de l'API.
    Vérifie la connexion à la base de données.
    """
    try:
        # Tente une requête simple sur la base de données
        db.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

