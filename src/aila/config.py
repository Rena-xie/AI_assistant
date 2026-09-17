import os
from pathlib import Path

from dotenv import load_dotenv


# Resolve the project root from this file (src/aila/config.py -> project root),
# so the .env file is found no matter which directory Python is started from.
# parents[0] = src/aila, parents[1] = src, parents[2] = project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    PROJECT_ROOT / ".env"
)


def get_required_env(name: str) -> str:
    """Read a required environment variable.

    Raises:
        RuntimeError: if the variable is missing or empty, with a hint about
            how to configure it.
    """

    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Copy {PROJECT_ROOT / '.env.example'} to {PROJECT_ROOT / '.env'} "
            f"and fill in your values."
        )

    return value


OPENAI_API_KEY = get_required_env(
    "OPENAI_API_KEY"
)

OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL",
    "https://api.openai.com/v1"
)

MODEL_NAME = get_required_env(
    "MODEL_NAME"
)