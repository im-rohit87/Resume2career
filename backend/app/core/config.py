import os
from pathlib import Path
from dotenv import load_dotenv

# Locate .env file (check current directory and parent directory)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


class Settings:
    PROJECT_NAME: str = "Resume2Interview AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "An Intelligent Resume Analysis and Adaptive Mock Interview System"
    API_PREFIX: str = "/api"

    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "b39a48f07b9a2c4e61f2518e39029a8f4c2e11893a7d5b8c2e0149a7f36c2e81"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./resume2interview.db")

    # File uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "5"))
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx"}
    ALLOWED_MIME_TYPES: set = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "application/octet-stream",  # Fallback often sent by browsers for binary files
    }

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]

    # LLM Settings
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")


settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
