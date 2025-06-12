from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class CVFile(Base):
    """
    Modèle de base de données pour la table 'cv_files'.
    Représente les fichiers CV uploadés par les utilisateurs.
    """
    __tablename__ = "cv_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    filename = Column(String, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    # Statut du traitement du CV (ex: 'uploaded', 'parsing', 'parsed', 'recommended', 'failed')
    status = Column(String, default="uploaded", nullable=False)
    file_path = Column(String, nullable=False) # Le chemin absolu ou relatif où le fichier est stocké

    owner = relationship("User", back_populates="cv_files")
    parsed_cv = relationship("ParsedCV", back_populates="cv_file", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="cv_file", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="cv_file", cascade="all, delete-orphan")


class ParsedCV(Base):
    """
    Modèle de base de données pour la table 'parsed_cvs'.
    Stocke les données structurées et le texte brut extraites du CV.
    """
    __tablename__ = "parsed_cvs" #è Nom de la table dans la BDD

    id = Column(Integer, primary_key=True, index=True)
    cv_file_id = Column(Integer, ForeignKey("cv_files.id"), unique=True, nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_data = Column(JSON, nullable=True)
    processing_date = Column(DateTime(timezone=True), server_default=func.now())
    cv_file = relationship("CVFile", back_populates="parsed_cv")
