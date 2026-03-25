import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration (Together AI - Free Tier)
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))

# Scoring Configuration
SCORE_WEIGHTS = {
    "skill_match": 0.35,
    "experience_relevance": 0.25,
    "education_fit": 0.15,
    "role_alignment": 0.15,
    "overall_impression": 0.10,
}

# Thresholds
SHORTLIST_THRESHOLD = 70  # Minimum score to shortlist
RISK_FLAG_THRESHOLD = 40  # Below this triggers risk flags

# File upload settings
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_MB = 10
