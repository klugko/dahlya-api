from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """Schéma pour un jeton d'accès."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schéma pour les données contenues dans le jeton (subject)."""
    username: Optional[str] = None
