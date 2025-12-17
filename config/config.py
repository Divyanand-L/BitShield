"""
Configuration settings for the BitShield Procurement Agent
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
CACHE_DIR = DATA_DIR / "cache"
MODELS_DIR = DATA_DIR / "models"

# Create directories if they don't exist
for directory in [DATA_DIR, UPLOADS_DIR, CACHE_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# LangSmith Configuration
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "bitshield-procurement")

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_TENDER_FILE_SIZE_MB = int(os.getenv("MAX_TENDER_FILE_SIZE_MB", "50"))

# Risk Thresholds
RISK_THRESHOLDS = {
    "price_anomaly": {
        "high": 0.8,
        "medium": 0.5,
        "low": 0.3
    },
    "document_similarity": {
        "high": 0.9,
        "medium": 0.7,
        "low": 0.5
    },
    "relationship_score": {
        "high": 0.75,
        "medium": 0.5,
        "low": 0.25
    },
    "stylometry": {
        "high": 0.85,
        "medium": 0.65,
        "low": 0.45
    }
}

# Analysis Parameters
MIN_BIDDERS_FOR_COLLUSION = 2
STATISTICAL_SIGNIFICANCE_LEVEL = 0.05
PRICE_OUTLIER_STD_THRESHOLD = 2.0

# Models
SBERT_MODEL = "all-MiniLM-L6-v2"
SPACY_MODEL = "en_core_web_sm"
