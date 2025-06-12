from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserInDB, UserLogin
from app.schemas.token import Token
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_user
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Enregistre un nouvel utilisateur.
    """
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà."
        )

    hashed_password = get_password_hash(user_in.password)
    # Met à jour la création de l'utilisateur pour inclure fullname
    db_user = User(
        email=user_in.email,
        password_hash=hashed_password,
        fullname=user_in.fullname
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Connecte un utilisateur et retourne un jeton d'accès JWT.
    Attend l'email et le mot de passe dans le corps de la requête JSON.
    """
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user or not verify_password(user_login.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Récupère les informations de l'utilisateur actuellement authentifié.
    """
    return current_user
