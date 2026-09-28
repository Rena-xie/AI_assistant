from __future__ import annotations

import json
from typing import Any

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from ..memory.learning import LearningService


def _extract_user_id(config: RunnableConfig | None) -> str | None:
    if not isinstance(config, dict):
        return None
    configurable = config.get("configurable")
    if not isinstance(configurable, dict):
        return None
    user_id = configurable.get("user_id")
    return str(user_id) if user_id else None


def _parse_json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (dict, list, tuple, set)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ""
        try:
            return json.loads(text)
        except (TypeError, ValueError):
            return text
    return value


@tool
async def get_learning_status(user_id: str | None = None, config: RunnableConfig | None = None) -> str:
    """Read the user's structured learning state across threads.

    This is deliberately lightweight. It exposes the current goal, skill state,
    project progress, current plan, and known weaknesses for the user.
    """
    resolved_user_id = user_id or _extract_user_id(config)
    if not resolved_user_id:
        return "No user_id available for learning status lookup."

    try:
        service = LearningService()
        status = await service.get_learning_status(resolved_user_id)
        return json.dumps(status, ensure_ascii=False, sort_keys=True)
    except Exception as exc:
        return f"Learning status lookup failed: {exc}"


@tool
async def update_learning_status(
    action: str,
    user_id: str | None = None,
    config: RunnableConfig | None = None,
    goal_key: str | None = None,
    goal_value: str | None = None,
    skill_key: str | None = None,
    skill_value: str | None = None,
    project_key: str | None = None,
    project_value: str | None = None,
    plan_key: str | None = None,
    plan_value: str | None = None,
    weakness_key: str | None = None,
    weakness_value: str | None = None,
    payload: str | None = None,
) -> str:
    """Update the user's structured learning state.

    Supported actions:
    - set_goal
    - update_skill
    - update_project
    - update_plan
    - update_weakness
    """
    resolved_user_id = user_id or _extract_user_id(config)
    if not resolved_user_id:
        return "No user_id available for learning status update."

    try:
        service = LearningService()
        action_name = (action or "").strip()

        if action_name == "set_goal":
            if not goal_key:
                goal_key = "primary_goal"
            if not goal_value:
                goal_value = payload if payload is not None else ""
            if not goal_value:
                return "goal_value is required for set_goal."
            updated = await service.update_goal(resolved_user_id, goal_key, goal_value)
            return json.dumps(updated, ensure_ascii=False, sort_keys=True)

        if action_name == "update_skill":
            if not skill_key:
                return "skill_key is required for update_skill."
            parsed_value = _parse_json_value(skill_value if skill_value is not None else payload)
            updated = await service.update_skill(resolved_user_id, skill_key, parsed_value)
            return json.dumps(updated, ensure_ascii=False, sort_keys=True)

        if action_name == "update_project":
            if not project_key:
                return "project_key is required for update_project."
            parsed_value = _parse_json_value(project_value if project_value is not None else payload)
            updated = await service.update_project(resolved_user_id, project_key, parsed_value)
            return json.dumps(updated, ensure_ascii=False, sort_keys=True)

        if action_name == "update_plan":
            key = plan_key or "current_plan"
            parsed_value = _parse_json_value(plan_value if plan_value is not None else payload)
            updated = await service.update_plan(resolved_user_id, key, parsed_value)
            return json.dumps(updated, ensure_ascii=False, sort_keys=True)

        if action_name == "update_weakness":
            if not weakness_key:
                return "weakness_key is required for update_weakness."
            parsed_value = _parse_json_value(weakness_value if weakness_value is not None else payload)
            updated = await service.update_weakness(resolved_user_id, weakness_key, parsed_value)
            return json.dumps(updated, ensure_ascii=False, sort_keys=True)

        return (
            "Unsupported action. Use one of: set_goal, update_skill, update_project, "
            "update_plan, update_weakness."
        )
    except Exception as exc:
        return f"Learning status update failed: {exc}"
