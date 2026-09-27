from pathlib import Path
import os
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

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