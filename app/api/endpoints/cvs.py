from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.cv import CVFile

router = APIRouter()

@router.post("/upload/")
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint pour uploader un fichier CV (PDF ou DOCX).
    Cette implémentation est basique et sera étoffée dans la prochaine itération.
    """
    # Vérification basique du type de fichier
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF et DOCX sont acceptés.")

    # Dans cette itération, nous allons juste simuler l'enregistrement.
    # Le stockage réel et le traitement seront ajoutés plus tard.
    try:
        # Crée une entrée dans la base de données pour le fichier CV
        cv_file = CVFile(
            filename=file.filename,
            status="uploaded",
            file_path=f"/tmp/cv_files/{file.filename}" # Chemin temporaire fictif
        )
        db.add(cv_file)
        db.commit()
        db.refresh(cv_file)

        # Simuler le stockage du fichier
        # with open(cv_file.file_path, "wb") as buffer:
        #     shutil.copyfileobj(file.file, buffer)

        return {"message": f"Fichier '{file.filename}' uploadé avec succès et enregistré en base de données.", "cv_id": cv_file.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload du fichier : {e}")

@router.get("/{cv_id}/status/")
def get_cv_status(cv_id: int, db: Session = Depends(get_db)):
    """
    Endpoint pour vérifier le statut de traitement d'un CV.
    """
    cv_file = db.query(CVFile).filter(CVFile.id == cv_id).first()
    if not cv_file:
        raise HTTPException(status_code=404, detail="CV non trouvé.")
    return {"cv_id": cv_file.id, "filename": cv_file.filename, "status": cv_file.status, "upload_date": cv_file.upload_date}
