"""Short-term conversation memory.

A conversation ("chat window") is identified by a LangGraph ``thread_id``.
It is not a user id: this is a single-user assistant, so there is no user
system, no multi-user isolation, and no long-term memory.
"""

from .checkpoint import DEFAULT_THREAD_ID, create_checkpointer, get_checkpointer


__all__ = [
    "DEFAULT_THREAD_ID",
    "create_checkpointer",
    "get_checkpointer",
]