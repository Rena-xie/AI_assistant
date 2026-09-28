from pathlib import Path
import os
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = (PROJECT_ROOT / "data").resolve()
CHECKPOINT_DB_PATH = (PROJECT_ROOT / "data" / "checkpoints.sqlite").resolve()
MEMORY_DB_PATH = (PROJECT_ROOT / "data" / "memory.sqlite").resolve()

DATA_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(PROJECT_ROOT / ".env")


OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL"
)

MODEL_NAME = os.getenv(
    "MODEL_NAME"
)

DASHSCOPE_API_KEY = os.getenv(
    "DASHSCOPE_API_KEY"
)

# Web search tool backend: "bing" (default), "duckduckgo" or "mock" (offline).
WEB_SEARCH_BACKEND = os.getenv(
    "WEB_SEARCH_BACKEND"
)
