from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Feedback(Base):
    """
    Modèle de base de données pour la table 'feedbacks'.
    Permet aux utilisateurs de laisser des retours sur les recommandations.
    """
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    cv_file_id = Column(Integer, ForeignKey("cv_files.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Peut être NULL si anonyme
    rating = Column(Integer, nullable=True) # Note (ex: de 1 à 5)
    comments = Column(Text, nullable=True) # Commentaires textuels
    feedback_date = Column(DateTime(timezone=True), server_default=func.now())

    cv_file = relationship("CVFile", back_populates="feedbacks")
    user = relationship("User") # Relation simple avec l'utilisateur, pas de back_populates ici
