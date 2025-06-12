import os
import shutil
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.cv import CVFile, ParsedCV
from app.models.user import User # Importe le modèle User
from app.services.cv_parser import cv_parser_service
from app.core.config import settings
from app.core.security import get_current_user # Importe la dépendance pour l'utilisateur courant
from typing import Optional, List

router = APIRouter()

@router.post("/upload/", status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user) # Utilisateur courant (peut être None si non connecté)
):
    """
    Endpoint pour uploader un fichier CV (PDF ou DOCX), le stocker,
    et extraire son texte brut pour le sauvegarder en base de données.
    Associe le CV à l'utilisateur si authentifié.
    """
    allowed_content_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seuls les fichiers PDF et DOCX sont acceptés."
        )

    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)

    file_extension = file.filename.split(".")[-1] if "." in file.filename else "tmp"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_location = os.path.join(upload_dir, unique_filename)

    cv_file_db = None

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        cv_file_db = CVFile(
            filename=file.filename,
            file_path=file_location,
            status="uploaded",
            user_id=current_user.id if current_user else None # Associe l'ID de l'utilisateur si connecté
        )
        db.add(cv_file_db)
        db.commit()
        db.refresh(cv_file_db)

        raw_text = cv_parser_service.extract_raw_text(file_location, file.content_type)

        if raw_text:
            parsed_cv_db = ParsedCV(
                cv_file_id=cv_file_db.id,
                raw_text=raw_text,
                parsed_data={}
            )
            db.add(parsed_cv_db)
            cv_file_db.status = "parsed"
            db.commit()
            db.refresh(parsed_cv_db)
            db.refresh(cv_file_db)

            return {
                "message": f"Fichier '{file.filename}' uploadé et texte extrait avec succès.",
                "cv_id": cv_file_db.id,
                "filename": cv_file_db.filename,
                "status": cv_file_db.status,
                "extracted_text_preview": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
            }
        else:
            cv_file_db.status = "parsing_failed"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de l'extraction du texte du CV '{file.filename}'. Le fichier a été enregistré mais non traité."
            )

    except Exception as e:
        db.rollback()
        if os.path.exists(file_location):
            os.remove(file_location)
        if cv_file_db:
            cv_file_db.status = "upload_failed"
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur inattendue est survenue lors du traitement du CV: {e}"
        )

@router.get("/{cv_id}/status/", response_model=dict)
def get_cv_status(
    cv_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user) # Optionnel, pour le cas où le CV est privé
):
    """
    Endpoint pour vérifier le statut de traitement d'un CV.
    Si l'utilisateur est authentifié, vérifie la propriété du CV.
    """
    cv_file = db.query(CVFile).filter(CVFile.id == cv_id).first()
    if not cv_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV non trouvé.")

    # Si le CV a un propriétaire et que l'utilisateur n'est pas le propriétaire
    if cv_file.user_id is not None and (current_user is None or cv_file.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé à ce CV.")

    response_data = {
        "cv_id": cv_file.id,
        "filename": cv_file.filename,
        "status": cv_file.status,
        "upload_date": cv_file.upload_date.isoformat() if cv_file.upload_date else None,
        "extracted_text_preview": None
    }

    if cv_file.status == "parsed":
        parsed_cv = db.query(ParsedCV).filter(ParsedCV.cv_file_id == cv_file.id).first()
        if parsed_cv and parsed_cv.raw_text:
            response_data["extracted_text_preview"] = parsed_cv.raw_text[:500] + "..." if len(parsed_cv.raw_text) > 500 else parsed_cv.raw_text

    return response_data

@router.get("/my-cvs", response_model=List[dict]) # On peut affiner le response_model avec un Pydantic Model de CVFile simplifié
async def get_my_cvs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Nécessite un utilisateur authentifié
):
    """
    Endpoint pour qu'un utilisateur authentifié puisse voir la liste de ses CVs uploadés.
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentification requise.")

    # Récupère tous les CVs appartenant à l'utilisateur actuel
    user_cv_files = db.query(CVFile).filter(CVFile.user_id == current_user.id).all()

    # Formate la réponse pour inclure les informations pertinentes
    response_list = []
    for cv_file in user_cv_files:
        response_data = {
            "cv_id": cv_file.id,
            "filename": cv_file.filename,
            "upload_date": cv_file.upload_date.isoformat() if cv_file.upload_date else None,
            "status": cv_file.status
        }
        response_list.append(response_data)
    return response_list
