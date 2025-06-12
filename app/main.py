from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.api_router import api_router
from app.db.session import get_db
from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware # Importe le middleware CORS

# Crée les tables dans la base de données (pour le développement initial).
# En production, vous utiliserez Alembic pour les migrations.
# Base.metadata.create_all(bind=engine)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API d'Orientation Professionnelle",
    description="API pour analyser les CV et générer des recommandations professionnelles.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
# Liste des origines autorisées (domaines et ports de votre frontend)
# IMPORTANT: Pour la production, listez explicitement vos domaines frontend.
# Évitez "*" en production si vous avez des données sensibles.
origins = [
    "http://localhost:5173",  # L'URL de votre frontend Vite par défaut
    "http://127.0.0.1:5173",  # Souvent nécessaire car 127.0.0.1 est différent de localhost pour les navigateurs
    "https://dahlya.vercel.app",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Liste des origines autorisées
    allow_credentials=True, # Autorise l'inclusion des cookies dans les requêtes cross-origin
    allow_methods=["*"], # Autorise toutes les méthodes (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Autorise tous les en-têtes dans les requêtes cross-origin
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
        db.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

