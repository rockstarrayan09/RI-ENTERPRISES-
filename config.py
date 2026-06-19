import os
from pathlib import Path


from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads" / "certificates"
EXCEL_PATH = DATA_DIR / "records.xlsx"
DB_PATH = DATA_DIR / "services.db"

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production").strip()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123").strip()

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

COMPANY_NAME = "RI ENTERPRISES"
FOUNDER_NAME = "RAFEEQ AHMED HUSSAIN"
COMPANY_TAGLINE = "Your trusted partner for online government services"

HOST = os.getenv("HOST", "0.0.0.0").strip()
PORT = int(os.getenv("PORT", "5000").strip())
AUTOSTART = os.getenv("AUTOSTART", "0").strip() == "1"
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0" if AUTOSTART else "1").strip() == "1"
