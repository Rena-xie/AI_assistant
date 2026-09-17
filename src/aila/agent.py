"""Minimal agent factory for the AI Learning Assistant.

This module is deliberately kept small:

- it only wires up an OpenAI-compatible chat model from configuration,
- it registers no tools and no agent loop yet.

`create_agent()` therefore returns a `ChatOpenAI` chat model object. Tools and
an agent runtime (for example a LangGraph ReAct loop) are added later.
"""

from langchain_openai import ChatOpenAI

from .config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    MODEL_NAME
)


def create_agent():
    """Create the chat model used by the assistant.

    Any OpenAI-compatible endpoint works (DeepSeek, DashScope, OpenAI, local
    Ollama, ...) because the base URL and the model name come from `.env`.

    Returns:
        ChatOpenAI: the configured chat model.
    """

    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        temperature=0.7
    )

    return llm