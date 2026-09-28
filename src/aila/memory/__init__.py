"""Conversation persistence helpers for the assistant.

This phase keeps thread state in the LangGraph SQLite checkpointer and stores
user-to-thread metadata in the app-level SQLite repository. No fake or
placeholder store is used.
"""

from .checkpoint import DEFAULT_THREAD_ID, close_checkpointer, create_checkpointer, get_checkpointer, open_checkpointer
from .repository import ConversationRepository


__all__ = [
    "DEFAULT_THREAD_ID",
    "create_checkpointer",
    "get_checkpointer",
    "open_checkpointer",
    "close_checkpointer",
    "ConversationRepository",
]