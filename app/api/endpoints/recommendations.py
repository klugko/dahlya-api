from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.cv import CVFile, ParsedCV
from app.models.recommendation import Recommendation
from app.services.recommendation_engine import recommendation_engine_service
from app.schemas.recommendation import RecommendationCreate, RecommendationInDB
from typing import List

router = APIRouter()

@router.post("/generate/{cv_id}", response_model=RecommendationInDB, status_code=status.HTTP_201_CREATED)
async def generate_recommendations_for_cv(
    cv_id: int,
    db: Session = Depends(get_db)
):
    """
    Endpoint pour générer des recommandations professionnelles pour un CV donné.
    Récupère le texte brut du CV, l'envoie à l'API GPT-4o et stocke les recommandations.
    """
    # 1. Vérifier si le CV existe et a été parsé
    cv_file = db.query(CVFile).filter(CVFile.id == cv_id).first()
    if not cv_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fichier CV non trouvé."
        )

    parsed_cv = db.query(ParsedCV).filter(ParsedCV.cv_file_id == cv_file.id).first()
    if not parsed_cv or not parsed_cv.raw_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le texte brut du CV n'est pas disponible ou n'a pas été parsé."
        )

    # 2. Vérifier si des recommandations existent déjà pour ce CV
    existing_recommendation = db.query(Recommendation).filter(Recommendation.cv_file_id == cv_id).first()
    if existing_recommendation:
        print(f"Recommandations existantes trouvées pour le CV {cv_id}. Retourne les recommandations existantes.")
        return existing_recommendation

    # 3. Générer les recommandations via le service d'IA
    try:
        recommendations_data = recommendation_engine_service.generate_recommendations(
            cv_raw_text=parsed_cv.raw_text
        )

        if not recommendations_data:
            # Met à jour le statut du CV en cas d'échec de la génération
            cv_file.status = "recommendation_failed"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Échec de la génération des recommandations par l'IA."
            )

        # 4. Sauvegarder les recommandations dans la base de données
        recommendation_db = Recommendation(
            cv_file_id=cv_id,
            job_type=recommendations_data.get("job_type"),
            environment=recommendations_data.get("environment"),
            suggested_trainings=recommendations_data.get("suggested_trainings"),
            skills_to_develop=recommendations_data.get("skills_to_develop")
        )
        db.add(recommendation_db)
        cv_file.status = "recommended" # Met à jour le statut du CVFile
        db.commit()
        db.refresh(recommendation_db)
        db.refresh(cv_file)

        return recommendation_db

    except Exception as e:
        db.rollback() # Annule les modifications en cas d'erreur
        # Met à jour le statut du CV en cas d'échec de la génération
        cv_file.status = "recommendation_failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération ou de la sauvegarde des recommandations: {e}"
        )

@router.get("/{cv_id}/", response_model=RecommendationInDB)
def get_recommendations_for_cv(
    cv_id: int,
    db: Session = Depends(get_db)
):
    """
    Endpoint pour récupérer les recommandations générées pour un CV spécifique.
    """
    recommendation = db.query(Recommendation).filter(Recommendation.cv_file_id == cv_id).first()
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommandations non trouvées pour ce CV."
        )
    return recommendation

@router.get("/", response_model=List[RecommendationInDB])
def get_all_recommendations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Endpoint pour récupérer toutes les recommandations (avec pagination).
    """
    recommendations = db.query(Recommendation).offset(skip).limit(limit).all()
    return recommendations
