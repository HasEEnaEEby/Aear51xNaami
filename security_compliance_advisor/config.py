import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).parent

# Data directories
DATA_DIR = BASE_DIR / "data"
FRAMEWORKS_DIR = DATA_DIR / "frameworks"
MAPPINGS_DIR = DATA_DIR / "mappings"
POLICIES_DIR = DATA_DIR / "policies"
MODELS_DIR = DATA_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"

# Create directories if they don't exist
os.makedirs(FRAMEWORKS_DIR, exist_ok=True)
os.makedirs(MAPPINGS_DIR, exist_ok=True)
os.makedirs(POLICIES_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Application settings
APP_NAME = "Security & Compliance Advisor"
APP_VERSION = "0.1.0"
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# API settings (if needed)
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Streamlit settings
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

# Model settings
DEFAULT_MODEL_PATH = os.getenv("MODEL_PATH", str(MODELS_DIR / "risk_scoring_model.pkl"))

# Risk scoring settings
RISK_CATEGORY_WEIGHTS = {
    "access_control": 0.25,
    "data_protection": 0.20,
    "network_security": 0.15,
    "vulnerability_management": 0.15,
    "incident_response": 0.15,
    "vendor_management": 0.10
}

# Supported frameworks
SUPPORTED_FRAMEWORKS = [
    "iso27001",
    "nist_csf",
    "gdpr",
    "hipaa",
    "pci_dss"
]

# File settings
ALLOWED_EXTENSIONS = [".csv", ".xlsx", ".xlsm", ".xls", ".json"]
MAX_UPLOAD_SIZE_MB = 10  # Maximum file upload size in MB

# Security settings
AUTH_REQUIRED = os.getenv("AUTH_REQUIRED", "False").lower() in ("true", "1", "t")
API_KEY = os.getenv("API_KEY", None)

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "app.log"))