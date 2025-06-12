import os
import pdfplumber
from docx import Document
from typing import Optional

class CVParserService:
    """
    Service pour extraire le texte des fichiers CV (PDF et DOCX).
    """

    def _extract_text_from_pdf(self, file_path: str) -> Optional[str]:
        """
        Extrait le texte d'un fichier PDF.
        """
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or "" # Ajoute le texte de chaque page, gère les pages vides
            return text
        except Exception as e:
            print(f"Erreur lors de l'extraction PDF de {file_path}: {e}")
            return None

    def _extract_text_from_docx(self, file_path: str) -> Optional[str]:
        """
        Extrait le texte d'un fichier DOCX.
        """
        try:
            doc = Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return "\n".join(full_text)
        except Exception as e:
            print(f"Erreur lors de l'extraction DOCX de {file_path}: {e}")
            return None

    def extract_raw_text(self, file_path: str, file_type: str) -> Optional[str]:
        """
        Méthode principale pour extraire le texte brut d'un CV en fonction de son type.
        """
        if file_type == "application/pdf":
            return self._extract_text_from_pdf(file_path)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return self._extract_text_from_docx(file_path)
        else:
            print(f"Type de fichier non supporté pour l'extraction: {file_type}")
            return None

cv_parser_service = CVParserService()
