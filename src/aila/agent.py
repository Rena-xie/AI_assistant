from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState

from .config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    MODEL_NAME
)

from .prompts.loader import build_runtime_system_prompt
from .tools import TOOLS
from .graph.router import route_question
from .rag import create_rag_chain
from .memory import create_checkpointer


def extract_question(state) -> str:
    """Return the text of the last message in the state."""

    messages = state["messages"]
    last_message = messages[-1]

    # Support both LangChain Message objects and plain dicts.
    if hasattr(last_message, "content"):
        return last_message.content

    if isinstance(last_message, dict):
        return last_message.get("content", "")

    return str(last_message)


def create_agent(checkpointer=None):
    if checkpointer is None:
        raise RuntimeError(
            "A LangGraph checkpointer must be supplied by the app lifespan; "
            "this project manages AsyncSqliteSaver lifecycle explicitly."
        )

    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        temperature=0.7
    )

    def runtime_prompt(_state=None, config=None):
        """Bind the governance prompt to the active runtime config.

        The learner memory is injected through LangGraph config rather than
        disguised as user text, so the model sees it as system/runtime context.
        """
        learning_context = ""
        if isinstance(config, dict):
            configurable = config.get("configurable") or {}
            learning_context = configurable.get("learning_context", "")
        return build_runtime_system_prompt(learning_context)

    # Inner react agent — unchanged tool-calling logic, but now using a real
    # system/runtime prompt instead of unstructured user-message concatenation.
    react_agent = create_react_agent(
        llm,
        tools=TOOLS,
        prompt=runtime_prompt,
    )

    # RAG chain — retrieval + grounded generation for knowledge questions.
    rag_chain = create_rag_chain()

    # --- Wrapper graph: router → (rag | agent) -----------------

    builder = StateGraph(MessagesState)

    def router_node(state):
        """Classify the question; no state mutation needed."""
        return {}

    def rag_node(state):
        """Knowledge path: answer only from the knowledge base."""
        question = extract_question(state)
        answer = rag_chain.invoke(question)
        return {"messages": [AIMessage(content=answer)]}

    def agent_node(state, config):
        """Chat path: delegate to the inner react agent."""
        result = react_agent.invoke(state, config=config)
        return {"messages": result["messages"]}

    builder.add_node("router", router_node)
    builder.add_node("rag", rag_node)
    builder.add_node("agent", agent_node)

    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router",
        route_question,
        {
            "knowledge": "rag",
            "chat": "agent",
        },
    )
    builder.add_edge("rag", END)
    builder.add_edge("agent", END)

    return builder.compile(
        checkpointer=checkpointer,
    )