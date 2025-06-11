from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Recommendation(Base):
    """
    Modèle de base de données pour la table 'recommendations'.
    Stocke les recommandations générées pour un CV.
    """
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    cv_file_id = Column(Integer, ForeignKey("cv_files.id"), nullable=False)
    job_type = Column(String, nullable=True) # Type de poste suggéré
    environment = Column(String, nullable=True) # Environnement de travail idéal
    suggested_trainings = Column(JSON, nullable=True) # Formations complémentaires utiles (liste JSON)
    skills_to_develop = Column(JSON, nullable=True) # Compétences à développer (liste JSON)
    generation_date = Column(DateTime(timezone=True), server_default=func.now())

    cv_file = relationship("CVFile", back_populates="recommendations")
