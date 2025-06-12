from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.cv import CVFile, ParsedCV
from app.models.recommendation import Recommendation
from app.models.user import User # Importe le modèle User
from app.services.recommendation_engine import recommendation_engine_service
from app.schemas.recommendation import RecommendationCreate, RecommendationInDB
from app.core.security import get_current_user # Importe la dépendance pour l'utilisateur courant
from typing import List, Optional

router = APIRouter()

@router.post("/generate/{cv_id}", response_model=RecommendationInDB, status_code=status.HTTP_201_CREATED)
async def generate_recommendations_for_cv(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user) # Optionnel, mais pour vérifier la propriété
):
    """
    Endpoint pour générer des recommandations professionnelles pour un CV donné.
    Vérifie la propriété du CV si l'utilisateur est authentifié.
    """
    cv_file = db.query(CVFile).filter(CVFile.id == cv_id).first()
    if not cv_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fichier CV non trouvé."
        )

    # Si le CV a un propriétaire et que l'utilisateur n'est pas le propriétaire
    if cv_file.user_id is not None and (current_user is None or cv_file.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé à ce CV.")

    parsed_cv = db.query(ParsedCV).filter(ParsedCV.cv_file_id == cv_file.id).first()
    if not parsed_cv or not parsed_cv.raw_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le texte brut du CV n'est pas disponible ou n'a pas été parsé."
        )

    existing_recommendation = db.query(Recommendation).filter(Recommendation.cv_file_id == cv_id).first()
    if existing_recommendation:
        print(f"Recommandations existantes trouvées pour le CV {cv_id}. Retourne les recommandations existantes.")
        return existing_recommendation

    try:
        recommendations_data = recommendation_engine_service.generate_recommendations(
            cv_raw_text=parsed_cv.raw_text
        )

        if not recommendations_data:
            cv_file.status = "recommendation_failed"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Échec de la génération des recommandations par l'IA."
            )

        recommendation_db = Recommendation(
            cv_file_id=cv_id,
            job_type=recommendations_data.get("job_type"),
            environment=recommendations_data.get("environment"),
            suggested_trainings=recommendations_data.get("suggested_trainings"),
            skills_to_develop=recommendations_data.get("skills_to_develop")
        )
        db.add(recommendation_db)
        cv_file.status = "recommended"
        db.commit()
        db.refresh(recommendation_db)
        db.refresh(cv_file)

        return recommendation_db

    except Exception as e:
        db.rollback()
        cv_file.status = "recommendation_failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération ou de la sauvegarde des recommandations: {e}"
        )

@router.get("/{cv_id}/", response_model=RecommendationInDB)
def get_recommendations_for_cv(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user) # Optionnel, pour vérifier la propriété
):
    """
    Endpoint pour récupérer les recommandations générées pour un CV spécifique.
    Vérifie la propriété du CV si l'utilisateur est authentifié.
    """
    recommendation = db.query(Recommendation).filter(Recommendation.cv_file_id == cv_id).first()
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommandations non trouvées pour ce CV."
        )

    # Vérifie la propriété du CV associé à la recommandation
    cv_file = db.query(CVFile).filter(CVFile.id == recommendation.cv_file_id).first()
    if cv_file and cv_file.user_id is not None and (current_user is None or cv_file.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé à ces recommandations.")

    return recommendation

@router.get("/", response_model=List[RecommendationInDB])
def get_all_recommendations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Seulement les recommandations de l'utilisateur authentifié
):
    """
    Endpoint pour récupérer toutes les recommandations de l'utilisateur actuellement authentifié.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentification requise.")

    recommendations = db.query(Recommendation)\
        .join(CVFile, Recommendation.cv_file_id == CVFile.id)\
        .filter(CVFile.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return recommendations
