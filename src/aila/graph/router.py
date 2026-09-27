"""Question router — classifies user messages by keyword matching."""


KNOWLEDGE_KEYWORDS = [
    "python",
    "langgraph",
    "langchain",
    "rag",
    "agent",
    "ai",
    "llm",
    "embedding",
    "vector",
    "向量",
    "知识库",
]


def route_question(state) -> str:
    """Classify the last user message as *knowledge* or *chat*.

    Parameters
    ----------
    state : dict
        LangGraph state containing a ``messages`` list.

    Returns
    -------
    str
        ``"knowledge"`` when any keyword matches, otherwise ``"chat"``.
    """

    messages = state["messages"]
    last_message = messages[-1]

    # Support both LangChain Message objects and plain dicts.
    if hasattr(last_message, "content"):
        text = last_message.content
    elif isinstance(last_message, dict):
        text = last_message.get("content", "")
    else:
        text = str(last_message)

    text_lower = text.lower()

    for keyword in KNOWLEDGE_KEYWORDS:
        if keyword in text_lower:
            return "knowledge"

    return "chat"
