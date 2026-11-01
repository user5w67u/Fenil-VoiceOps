import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DATASET_DIR = Path(os.getenv("DATASET_DIR", "../Capstone_Project_Dataset_FTTT_2026"))
if not DATASET_DIR.is_absolute():
    DATASET_DIR = (ROOT / DATASET_DIR).resolve()
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local").strip().lower()
LOCAL_MODEL_ID = os.getenv("LOCAL_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct").strip()
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
GNANI_API_KEY = os.getenv("GNANI_API_KEY", "").strip()
TOP_K = int(os.getenv("TOP_K", "5"))
