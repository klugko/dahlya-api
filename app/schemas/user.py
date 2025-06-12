from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Schéma de base pour un utilisateur."""
    email: EmailStr
    fullname: Optional[str] = None

class UserCreate(UserBase):
    """Schéma pour la création d'un nouvel utilisateur."""
    password: str

class UserLogin(UserBase):
    """Schéma pour la connexion d'un utilisateur."""
    password: str

class UserInDB(UserBase):
    """Schéma pour un utilisateur tel que stocké ou récupéré de la base de données."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
