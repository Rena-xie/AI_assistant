"""Load the runtime governance prompt used by the LangGraph agent.

This keeps the editable prompt text in ``system.md`` while also composing a
compact runtime summary from the three governance documents:

- learning_mission.md
- curriculum.md
- mentor_policy.md

The intent is to respect the project intent without copying the entire
curriculum into every message turn.
"""

from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PROMPTS_DIR.parents[3]
DOCS_DIR = PROJECT_ROOT / "docs"

SYSTEM_PROMPT_FILE = PROMPTS_DIR / "system.md"


def load_system_prompt() -> str:
    """Return the base prompt text from ``prompts/system.md``."""
    if not SYSTEM_PROMPT_FILE.is_file():
        raise FileNotFoundError(
            f"System prompt file not found: {SYSTEM_PROMPT_FILE}. "
            f"The prompt ships with the package; restore that file "
            f"or reinstall the project."
        )
    return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")


def _read_doc_text(filename: str) -> str:
    doc_path = DOCS_DIR / filename
    if not doc_path.is_file():
        return ""
    return doc_path.read_text(encoding="utf-8")


def _compact_doc_text(text: str, headings: tuple[str, ...], limit: int = 900) -> str:
    if not text:
        return ""

    lines = text.splitlines()
    selected: list[str] = []
    capture = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") and any(h.lower() in stripped.lower() for h in headings):
            capture = True
            selected.append(stripped)
            continue
        if capture:
            if stripped.startswith("#") and not any(h.lower() in stripped.lower() for h in headings):
                break
            selected.append(line)

    compact = "\n".join(selected).strip()
    if len(compact) > limit:
        compact = compact[:limit].rstrip() + "..."
    return compact


def build_runtime_system_prompt(learning_context: str | None = None) -> str:
    """Compose the compact runtime prompt used by the active LangGraph agent.

    The runtime prompt is intentionally small: it includes the core system prompt,
    the long-term mission, the curriculum guidance, and the mentor policy, while
    avoiding a full curriculum dump on every chat turn.
    """
    base_prompt = load_system_prompt()

    mission = _compact_doc_text(
        _read_doc_text("learning_mission.md"),
        (
            "## 1. Mission",
            "## 2. Target Capability",
            "## 4. Work-Readiness Definition",
            "## 5. Learning Principles",
        ),
        limit=700,
    )

    curriculum = _compact_doc_text(
        _read_doc_text("curriculum.md"),
        (
            "# 2. Mastery Levels",
            "# 3. Capability Map",
            "# 4. C1 — Programming & Software Engineering",
            "# 5.",
        ),
        limit=700,
    )

    mentor = _compact_doc_text(
        _read_doc_text("mentor_policy.md"),
        (
            "# 2. Mentor Core Loop",
            "# 3. Mentor Priorities",
            "# 4. Diagnose Before Planning",
            "# 5. Teaching Mode Selection",
        ),
        limit=700,
    )

    blocks = [
        base_prompt,
        "## Governance: Mission",
        mission or "Mission: help the user grow into an AI application engineer through capability growth, evidence, and iterative practice.",
        "## Governance: Curriculum Guidance",
        curriculum or "Curriculum guidance: evaluate current capability by L0-L5 mastery, focus on core capability domains, and choose the next learning step based on evidence.",
        "## Governance: Mentor Policy",
        mentor or "Mentor policy: diagnose before planning, prefer long-term capability growth over answer completeness, and tailor teaching mode to current learner ability.",
    ]

    if learning_context:
        blocks.append("## Runtime learner context")
        blocks.append(learning_context.strip())

    return "\n\n".join(blocks).strip()