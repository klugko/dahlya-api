import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Classe de configuration pour l'application.
    Charge les variables d'environnement.
    """
    # Configuration du modèle Pydantic pour lire les variables d'environnement
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # URL de la base de données PostgreSQL
    # Exemple: postgresql://user:password@host:port/dbname
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Clé secrète pour le hachage des mots de passe ou la génération de tokens JWT
    # Il est crucial de la définir dans votre fichier .env et de ne jamais la commiter.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_super_secret_key")

    # Algorithme utilisé pour le chiffrement des tokens JWT
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # Durée de vie des tokens d'accès (en minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Instancie la classe Settings pour une utilisation facile dans l'application
settings = Settings()

