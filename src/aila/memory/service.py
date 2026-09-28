import json
from typing import Any

from .repository import MemoryRepository


ALLOWED_MEMORY_TYPES = {"profile", "goal", "skill", "project", "plan", "weakness"}


class MemoryService:
    """User-scoped long-term learning memory service.

    This service is intentionally simple and follows the project's current
    SQLite architecture: memory is persisted in the same `data/memory.sqlite`
    database, keyed by `user_id`, and is shared across threads.
    """

    def __init__(self, repository: MemoryRepository | None = None):
        self.repository = repository or MemoryRepository()

    def _normalize_memory_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (dict, list, tuple, set)):
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        return str(value)

    def _parse_memory_value(self, value: str) -> Any:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return ""
        try:
            parsed = json.loads(text)
            if isinstance(parsed, (dict, list)):
                return parsed
        except (TypeError, ValueError):
            pass
        return text

    async def get_memory(self, user_id: str, memory_type: str, memory_key: str):
        if not user_id:
            return None
        if memory_type not in ALLOWED_MEMORY_TYPES:
            return None
        row = await self.repository.get_memory(user_id, memory_type, memory_key)
        if row is None:
            return None
        row["memory_value"] = self._parse_memory_value(row.get("memory_value"))
        return row

    async def set_memory(self, user_id: str, memory_type: str, memory_key: str, memory_value: Any):
        if not user_id:
            raise ValueError("user_id is required")
        if memory_type not in ALLOWED_MEMORY_TYPES:
            raise ValueError(f"Unsupported memory_type: {memory_type}")
        if not memory_key:
            raise ValueError("memory_key is required")
        normalized_value = self._normalize_memory_value(memory_value)
        return await self.repository.set_memory(user_id, memory_type, memory_key, normalized_value)

    async def delete_memory(self, user_id: str, memory_type: str, memory_key: str):
        if not user_id:
            return False
        if memory_type not in ALLOWED_MEMORY_TYPES:
            return False
        return await self.repository.delete_memory(user_id, memory_type, memory_key)

    async def list_memories(self, user_id: str, memory_type: str | None = None):
        if not user_id:
            return []
        rows = await self.repository.list_memories(user_id, memory_type)
        for row in rows:
            row["memory_value"] = self._parse_memory_value(row.get("memory_value"))
        return rows

    async def build_memory_context(self, user_id: str) -> str:
        try:
            rows = await self.list_memories(user_id)
        except Exception:
            return ""

        if not rows:
            return ""

        grouped: dict[str, list[str]] = {"goal": [], "skill": [], "project": [], "plan": [], "weakness": [], "profile": []}

        for row in rows:
            memory_type = row.get("memory_type")
            memory_key = row.get("memory_key")
            memory_value = row.get("memory_value")
            if memory_type not in grouped:
                continue
            if memory_value is None:
                continue
            grouped.setdefault(memory_type, []).append(f"- {memory_key}: {memory_value}")

        sections = []
        for memory_type in ("profile", "goal", "skill", "project", "plan", "weakness"):
            items = grouped.get(memory_type, [])
            if not items:
                continue
            title = {
                "profile": "个人资料",
                "goal": "学习目标",
                "skill": "技能状态",
                "project": "项目进度",
                "plan": "当前计划",
                "weakness": "薄弱项",
            }[memory_type]
            sections.append(f"{title}:\n" + "\n".join(items))

        return "\n\n".join(sections)
