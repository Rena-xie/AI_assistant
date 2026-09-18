"""Load the system prompt from the ``prompts`` directory.

The prompt is stored as data in ``system.md`` next to this module, so it can
be edited without touching Python code.
"""

from pathlib import Path


# Directory of this module: src/aila/prompts/.
PROMPTS_DIR = Path(__file__).resolve().parent

# System prompt handed to the LangGraph agent by `aila.agent.create_agent()`.
SYSTEM_PROMPT_FILE = PROMPTS_DIR / "system.md"


def load_system_prompt() -> str:
    """Return the content of ``prompts/system.md``.

    The file is located relative to this module, so the function works no
    matter which directory Python was started from.

    Returns:
        The system prompt text.

    Raises:
        FileNotFoundError: if the prompt file is missing, so the failure
            names the exact path instead of surfacing later inside the agent.
    """

    if not SYSTEM_PROMPT_FILE.is_file():

        raise FileNotFoundError(
            f"System prompt file not found: {SYSTEM_PROMPT_FILE}. "
            f"The prompt ships with the package; restore that file "
            f"or reinstall the project."
        )

    return SYSTEM_PROMPT_FILE.read_text(
        encoding="utf-8"
    )