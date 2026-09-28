import json
from typing import Any

from .repository import MemoryRepository


ALLOWED_MEMORY_TYPES = {"goal", "skill", "project", "plan", "weakness"}


class LearningService:
    """User-scoped structured learning state service.

    This is a thin layer over the same user_memories table used by the broader
    long-term memory system. It focuses on structured learning information:
    goal, skill status, project progress, current plan, and weaknesses.
    """

    def __init__(self, repository: MemoryRepository | None = None):
        self.repository = repository or MemoryRepository()

    def _coerce_json(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (dict, list, tuple, set)):
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        return str(value)

    def _read_value(self, value: Any) -> Any:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return ""
        try:
            parsed = json.loads(text)
        except (TypeError, ValueError):
            return text
        return parsed

    def _normalize_skill_key(self, skill_key: str) -> str:
        return f"skill.{skill_key.strip().lower()}" if skill_key and not skill_key.lower().startswith("skill.") else skill_key.strip().lower()

    def _normalize_project_key(self, project_key: str) -> str:
        return f"project.{project_key.strip().lower()}" if project_key and not project_key.lower().startswith("project.") else project_key.strip().lower()

    def _normalize_weakness_key(self, weakness_key: str) -> str:
        return f"weakness.{weakness_key.strip().lower()}" if weakness_key and not weakness_key.lower().startswith("weakness.") else weakness_key.strip().lower()

    async def get_learning_snapshot(self, user_id: str) -> dict[str, Any]:
        if not user_id:
            return {
                "goal": {},
                "skills": {},
                "projects": {},
                "plan": {},
                "weaknesses": {},
            }

        rows = await self.repository.list_memories(user_id)
        snapshot = {
            "goal": {},
            "skills": {},
            "projects": {},
            "plan": {},
            "weaknesses": {},
        }

        for row in rows:
            memory_type = row.get("memory_type")
            memory_key = row.get("memory_key")
            value = self._read_value(row.get("memory_value"))
            if memory_type == "goal":
                snapshot["goal"][memory_key] = value
            elif memory_type == "skill":
                snapshot["skills"][memory_key] = value
            elif memory_type == "project":
                snapshot["projects"][memory_key] = value
            elif memory_type == "plan":
                snapshot["plan"][memory_key] = value
            elif memory_type == "weakness":
                snapshot["weaknesses"][memory_key] = value

        return snapshot

    async def update_goal(self, user_id: str, goal_key: str, goal_value: str) -> dict[str, Any]:
        if not user_id:
            raise ValueError("user_id is required")
        if not goal_key:
            raise ValueError("goal_key is required")
        if not goal_value:
            raise ValueError("goal_value is required")
        normalized_key = "primary_goal" if goal_key.strip().lower() in {"primary_goal", "goal", "main_goal"} else goal_key.strip()
        await self.repository.set_memory(user_id, "goal", normalized_key, self._coerce_json(goal_value))
        return await self.get_learning_snapshot(user_id)

    async def update_skill(self, user_id: str, skill_key: str, skill_value: dict[str, Any] | str):
        if not user_id:
            raise ValueError("user_id is required")
        if not skill_key:
            raise ValueError("skill_key is required")
        normalized_key = self._normalize_skill_key(skill_key)
        payload = skill_value if isinstance(skill_value, dict) else {"status": skill_value}
        await self.repository.set_memory(user_id, "skill", normalized_key, self._coerce_json(payload))
        return await self.get_learning_snapshot(user_id)

    async def update_project(self, user_id: str, project_key: str, project_value: dict[str, Any] | str):
        if not user_id:
            raise ValueError("user_id is required")
        if not project_key:
            raise ValueError("project_key is required")
        normalized_key = self._normalize_project_key(project_key)
        payload = project_value if isinstance(project_value, dict) else {"summary": project_value}
        await self.repository.set_memory(user_id, "project", normalized_key, self._coerce_json(payload))
        return await self.get_learning_snapshot(user_id)

    async def update_plan(self, user_id: str, plan_key: str, plan_value: dict[str, Any] | str):
        if not user_id:
            raise ValueError("user_id is required")
        if not plan_key:
            plan_key = "current_plan"
        payload = plan_value if isinstance(plan_value, dict) else {"summary": plan_value}
        await self.repository.set_memory(user_id, "plan", plan_key, self._coerce_json(payload))
        return await self.get_learning_snapshot(user_id)

    async def update_weakness(self, user_id: str, weakness_key: str, weakness_value: dict[str, Any] | str):
        if not user_id:
            raise ValueError("user_id is required")
        if not weakness_key:
            raise ValueError("weakness_key is required")
        normalized_key = self._normalize_weakness_key(weakness_key)
        payload = weakness_value if isinstance(weakness_value, dict) else {"summary": weakness_value}
        await self.repository.set_memory(user_id, "weakness", normalized_key, self._coerce_json(payload))
        return await self.get_learning_snapshot(user_id)

    async def get_learning_status(self, user_id: str) -> dict[str, Any]:
        return await self.get_learning_snapshot(user_id)
