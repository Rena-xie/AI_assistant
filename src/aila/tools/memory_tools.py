from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from ..memory.service import MemoryService


_ALLOWED_MEMORY_TYPES = {"profile", "goal", "skill", "project", "plan", "weakness"}


def _extract_user_id(config: RunnableConfig | None) -> str | None:
    if not isinstance(config, dict):
        return None
    configurable = config.get("configurable")
    if not isinstance(configurable, dict):
        return None
    user_id = configurable.get("user_id")
    return str(user_id) if user_id else None


@tool
async def get_learning_memory(
    memory_type: str = "all",
    user_id: str | None = None,
    config: RunnableConfig | None = None,
) -> str:
    """Read the user's cross-thread long-term learning memory.

    Use this when the user asks about their learning goal, current plans,
    project progress, skills, or weaknesses. This is a user-scoped memory, not
    a thread-scoped conversation history.

    Args:
        memory_type: one of profile|goal|skill|project|plan|weakness|all.
        user_id: optional explicit user identifier.
        config: injected runtime context from LangGraph.
    """
    resolved_user_id = user_id or _extract_user_id(config)
    if not resolved_user_id:
        return "No user_id available for long-term memory lookup."

    try:
        service = MemoryService()
        if memory_type == "all":
            rows = await service.list_memories(resolved_user_id)
            if not rows:
                return "No long-term learning memory found for this user."
            serialized = []
            for row in rows:
                serialized.append(
                    f"{row['memory_type']} / {row['memory_key']} = {row['memory_value']}"
                )
            return "\n".join(serialized)

        if memory_type not in _ALLOWED_MEMORY_TYPES:
            return "Unsupported memory_type. Allowed values: profile, goal, skill, project, plan, weakness, all."
        rows = await service.list_memories(resolved_user_id, memory_type)
        if not rows:
            return f"No {memory_type} memory found for this user."
        serialized = []
        for row in rows:
            serialized.append(f"{row['memory_key']} = {row['memory_value']}")
        return "\n".join(serialized)
    except Exception as exc:
        return f"Memory lookup failed: {exc}"


@tool
async def update_learning_memory(
    memory_type: str,
    memory_key: str,
    memory_value: str,
    user_id: str | None = None,
    config: RunnableConfig | None = None,
) -> str:
    """Persist a user-level learning fact that should survive across threads.

    Only stable learning facts should be saved here: goals, project progress,
    skills, plans, weaknesses, or profile facts. Do not save ordinary chat
    content, tool outputs, or ephemeral conversation details.

    Args:
        memory_type: one of profile|goal|skill|project|plan|weakness.
        memory_key: stable identifier such as primary_goal or rag_level.
        memory_value: structured value or plain string.
        user_id: optional explicit user identifier.
        config: injected runtime context from LangGraph.
    """
    resolved_user_id = user_id or _extract_user_id(config)
    if not resolved_user_id:
        return "No user_id available for long-term memory update."

    if memory_type not in _ALLOWED_MEMORY_TYPES:
        return "Unsupported memory_type. Allowed values: profile, goal, skill, project, plan, weakness."
    if not memory_key:
        return "memory_key is required."
    if memory_value is None:
        return "memory_value is required."

    try:
        service = MemoryService()
        await service.set_memory(resolved_user_id, memory_type, memory_key, memory_value)
        return f"Saved learning memory for user {resolved_user_id}: {memory_type}/{memory_key}"
    except Exception as exc:
        return f"Memory update failed: {exc}"
