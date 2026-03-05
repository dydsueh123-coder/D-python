import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    OUTPUT_FOLDER = BASE_DIR / "outputs"
    MAX_CONTENT_LENGTH = 220 * 1024 * 1024  # 220MB (docx 20 + images 200)
    ALLOWED_DOCX = {".docx"}
    ALLOWED_IMAGES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".gif"}

    @classmethod
    def ensure_dirs(cls):
        cls.UPLOAD_FOLDER.mkdir(exist_ok=True)
        cls.OUTPUT_FOLDER.mkdir(exist_ok=True)
