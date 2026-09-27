"""LangGraph checkpointer = the assistant's short-term memory.

Stage 1 uses the official ``MemorySaver`` checkpointer, so checkpoints live
in process memory only: the conversation survives as long as the process runs
and is gone after a restart. This is exactly the behavior wanted for a
single chat window and does not introduce any database or long-term memory.
"""

from langgraph.checkpoint.memory import MemorySaver


# One chat window for this personal assistant.
# A thread_id identifies a conversation, not a user.
DEFAULT_THREAD_ID = "default"


def create_checkpointer() -> MemorySaver:
    """Return the official in-memory LangGraph checkpointer."""
    return MemorySaver()


def get_checkpointer() -> MemorySaver:
    """Backward-compatible wrapper for existing imports."""
    return create_checkpointer()