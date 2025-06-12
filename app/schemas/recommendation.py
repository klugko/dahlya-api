# app/schemas/recommendation.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RecommendationBase(BaseModel):
    """Schéma de base pour les recommandations."""
    job_type: Optional[str] = Field(None, description="Type de poste suggéré basé sur l'analyse du CV.")
    environment: Optional[str] = Field(None, description="Environnement de travail idéal (ex: startup, grande entreprise, freelance, association).")
    suggested_trainings: Optional[List[str]] = Field(None, description="Liste des formations complémentaires ou certifications utiles.")
    skills_to_develop: Optional[List[str]] = Field(None, description="Liste des compétences clés à renforcer ou à acquérir.")

class RecommendationCreate(RecommendationBase):
    """Schéma pour la création de nouvelles recommandations."""
    cv_file_id: int # L'ID du fichier CV auquel cette recommandation appartient

class RecommendationInDB(RecommendationBase):
    """Schéma pour les recommandations récupérées de la base de données."""
    id: int
    cv_file_id: int
    generation_date: datetime

    class Config:
        # Permet à Pydantic de mapper les objets SQLAlchemy directement
        from_attributes = True
