from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from .config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    MODEL_NAME
)

from .tools import calculator


def create_agent():

    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        temperature=0.7
    )

    agent = create_react_agent(
        llm,
        tools=[
            calculator
        ]
    )

    return agent