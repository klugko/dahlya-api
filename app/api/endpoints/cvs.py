import os
import shutil
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.cv import CVFile, ParsedCV
from app.services.cv_parser import cv_parser_service
from app.core.config import settings

router = APIRouter()

@router.post("/upload/", status_code=status.HTTP_201_CREATED)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint pour uploader un fichier CV (PDF ou DOCX), le stocker,
    et extraire son texte brut pour le sauvegarder en base de données.
    """
    allowed_content_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seuls les fichiers PDF et DOCX sont acceptés."
        )

    # 1. Préparer le chemin de stockage du fichier
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True) # Crée le répertoire si non existant

    # Générer un nom de fichier unique pour éviter les conflits
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "tmp"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_location = os.path.join(upload_dir, unique_filename)

    cv_file_db = None # Variable pour stocker l'objet CVFile si une erreur survient

    try:
        # 2. Sauvegarder le fichier sur le système de fichiers
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. Enregistrer les métadonnées du fichier dans la base de données
        cv_file_db = CVFile(
            filename=file.filename,
            file_path=file_location, # Chemin réel du fichier stocké
            status="uploaded"
            # user_id sera ajouté plus tard avec l'authentification
        )
        db.add(cv_file_db)
        db.commit() # Commit pour obtenir l'ID du CVFile
        db.refresh(cv_file_db)

        # 4. Extraire le texte brut du CV
        raw_text = cv_parser_service.extract_raw_text(file_location, file.content_type)

        if raw_text:
            # 5. Sauvegarder le texte brut dans la table ParsedCV
            parsed_cv_db = ParsedCV(
                cv_file_id=cv_file_db.id,
                raw_text=raw_text,
                parsed_data={} # Initialise avec un objet JSON vide pour l'itération 3
            )
            db.add(parsed_cv_db)
            cv_file_db.status = "parsed" # Met à jour le statut du CVFile
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
            # Si l'extraction échoue, on marque le CVFile comme "failed"
            cv_file_db.status = "parsing_failed"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de l'extraction du texte du CV '{file.filename}'. Le fichier a été enregistré mais non traité."
            )

    except Exception as e:
        db.rollback() # Annule les modifications en cas d'erreur
        # Si une erreur survient, supprime le fichier uploadé s'il existe
        if os.path.exists(file_location):
            os.remove(file_location)
        # Met à jour le statut si cv_file_db a déjà été créé
        if cv_file_db:
            cv_file_db.status = "upload_failed"
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur inattendue est survenue lors du traitement du CV: {e}"
        )

@router.get("/{cv_id}/status/", response_model=dict) # Ajouté response_model pour la documentation
def get_cv_status(cv_id: int, db: Session = Depends(get_db)):
    """
    Endpoint pour vérifier le statut de traitement d'un CV.
    Retourne le statut actuel et un aperçu du texte extrait si disponible.
    """
    cv_file = db.query(CVFile).filter(CVFile.id == cv_id).first()
    if not cv_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV non trouvé.")

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
