import asyncio
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ..config import MEMORY_DB_PATH


class ConversationRepository:
    def __init__(self, db_path: str | Path = MEMORY_DB_PATH):
        self.db_path = Path(db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        await self.init_db()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def init_db(self):
        await asyncio.to_thread(self._initialize_db)

    def _initialize_db(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    thread_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_conversations_user_updated
                ON conversations(user_id, updated_at DESC)
                """
            )
            conn.commit()

    async def close(self):
        return None

    async def create_conversation(self, user_id: str, thread_id: str, title: str = "新对话"):
        now = datetime.now(timezone.utc).isoformat()
        async with self._lock:
            await asyncio.to_thread(
                self._create_conversation,
                user_id,
                thread_id,
                title,
                now,
            )
        return await self.get_conversation(thread_id, user_id)

    def _create_conversation(self, user_id: str, thread_id: str, title: str, now: str):
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO conversations (thread_id, user_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(thread_id) DO UPDATE SET
                    user_id=excluded.user_id,
                    title=excluded.title,
                    updated_at=excluded.updated_at
                """,
                (thread_id, user_id, title, now, now),
            )
            conn.commit()

    async def list_conversations(self, user_id: str):
        async with self._lock:
            rows = await asyncio.to_thread(self._list_conversations, user_id)
        return rows

    def _list_conversations(self, user_id: str):
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT thread_id, user_id, title, created_at, updated_at
                FROM conversations
                WHERE user_id = ?
                ORDER BY updated_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    async def get_conversation(self, thread_id: str, user_id: str):
        async with self._lock:
            row = await asyncio.to_thread(self._get_conversation, thread_id, user_id)
        return row

    def _get_conversation(self, thread_id: str, user_id: str):
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT thread_id, user_id, title, created_at, updated_at
                FROM conversations
                WHERE thread_id = ? AND user_id = ?
                LIMIT 1
                """,
                (thread_id, user_id),
            ).fetchone()
        return dict(row) if row is not None else None

    async def update_conversation(self, user_id: str, thread_id: str, title: str | None = None):
        now = datetime.now(timezone.utc).isoformat()
        async with self._lock:
            await asyncio.to_thread(self._update_conversation, user_id, thread_id, title, now)
        return await self.get_conversation(thread_id, user_id)

    def _update_conversation(self, user_id: str, thread_id: str, title: str | None, now: str):
        with sqlite3.connect(str(self.db_path)) as conn:
            existing = conn.execute(
                "SELECT title, created_at FROM conversations WHERE thread_id = ? AND user_id = ?",
                (thread_id, user_id),
            ).fetchone()
            if existing is None:
                created_at = now
                effective_title = title or "新对话"
            else:
                created_at = existing[1]
                effective_title = title or existing[0]

            conn.execute(
                """
                INSERT INTO conversations (thread_id, user_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(thread_id) DO UPDATE SET
                    title=excluded.title,
                    updated_at=excluded.updated_at
                """,
                (thread_id, user_id, effective_title, created_at, now),
            )
            conn.commit()
