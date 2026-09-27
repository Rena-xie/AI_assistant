"""Execution layer: the only place that touches the LangGraph call API.

It is also the only place that owns the LangGraph ``config``. Every graph call
must carry a ``thread_id`` now that a checkpointer is installed, because the
checkpointer uses it to decide *which conversation* the state belongs to.

``thread_id`` == one chat window. It is **not** a user id: this assistant is
single-user, so there is no user system and no multi-user isolation.
"""

from ..memory import DEFAULT_THREAD_ID


def run_agent(
    agent,
    message,
    thread_id: str = DEFAULT_THREAD_ID
):
    """Run one conversation turn and return the final assistant message.

    Parameters
    ----------
    agent :
        The compiled graph returned by ``aila.agent.create_agent()``.
    message : str
        The user message.
    thread_id : str
        Chat window id. Turns that share the same value share memory;
        turns with different values are independent conversations.
    """

    # LangGraph reads memory identity from this config.
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        },
        config=config
    )

    return result["messages"][-1]