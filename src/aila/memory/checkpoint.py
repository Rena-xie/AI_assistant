"""Persistent LangGraph checkpoint lifecycle.

This phase uses the SQLite-backed async LangGraph checkpointer only. The
thread checkpoint state is persisted in the database, while user/thread
metadata is stored in a separate app-level repository.
"""

from pathlib import Path

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from ..config import CHECKPOINT_DB_PATH


DEFAULT_THREAD_ID = "default"


def create_checkpointer() -> AsyncSqliteSaver:
    """Return the async context manager for the SQLite-backed checkpointer.

    The caller must enter the context before passing the saver instance to
    ``builder.compile(checkpointer=...)``.
    """
    db_path = Path(CHECKPOINT_DB_PATH).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return AsyncSqliteSaver.from_conn_string(str(db_path))


async def open_checkpointer():
    """Enter the AsyncSqliteSaver lifecycle and return the saver instance."""
    checkpointer_cm = create_checkpointer()
    saver = await checkpointer_cm.__aenter__()
    return checkpointer_cm, saver


async def close_checkpointer(checkpointer_cm):
    """Exit the AsyncSqliteSaver lifecycle and close SQLite resources."""
    if checkpointer_cm is not None:
        await checkpointer_cm.__aexit__(None, None, None)


def get_checkpointer():
    """Backward-compatible wrapper for imports that expect an active saver."""
    return create_checkpointer()