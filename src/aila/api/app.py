import json
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import HumanMessage

from ..agent import create_agent
from ..memory import close_checkpointer, open_checkpointer
from ..memory.repository import ConversationRepository
from .schemas import (
    ChatRequest,
    ChatResponse,
    ConversationCreateRequest,
)


def _normalize_user_id(user_id):
    value = (user_id or "local-user").strip()
    return value or "local-user"


def _normalize_thread_id(thread_id):
    value = (thread_id or "").strip()
    if value:
        return value
    return f"thread-{uuid4().hex}"


def _truncate_title(value, limit=36):
    text = str(value or "").strip()
    if not text:
        return "新对话"
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _normalize_source_entry(source_entry):
    if not isinstance(source_entry, dict):
        return None

    normalized = {}
    source_value = source_entry.get("source")
    if isinstance(source_value, str) and source_value:
        normalized["source"] = source_value
    elif isinstance(source_entry.get("file_name"), str) and source_entry.get("file_name"):
        normalized["source"] = source_entry["file_name"]
    elif isinstance(source_entry.get("title"), str) and source_entry.get("title"):
        normalized["source"] = source_entry["title"]

    if isinstance(source_entry.get("page"), (int, float)):
        normalized["page"] = source_entry["page"]
    if isinstance(source_entry.get("title"), str) and source_entry.get("title"):
        normalized["title"] = source_entry["title"]
    if isinstance(source_entry.get("file_name"), str) and source_entry.get("file_name"):
        normalized["file_name"] = source_entry["file_name"]

    if not normalized:
        return None
    return normalized


def _extract_tool_sources(message_chunk):
    if getattr(message_chunk, "type", None) != "tool":
        return []

    raw_content = getattr(message_chunk, "content", "")
    payload = raw_content

    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except (TypeError, ValueError):
            return []

    if isinstance(payload, dict):
        sources = payload.get("sources", [])
    elif isinstance(payload, list):
        sources = payload
    else:
        return []

    if not isinstance(sources, list):
        return []

    normalized = []
    seen = set()
    for item in sources:
        entry = _normalize_source_entry(item)
        if not entry:
            continue
        key = json.dumps(entry, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        normalized.append(entry)
    return normalized


def _extract_ai_answer(messages):
    for message in reversed(messages):
        if getattr(message, "type", None) == "ai":
            content = message.content
            if isinstance(content, list):
                return " ".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                )
            return str(content)

        if isinstance(message, dict) and message.get("type") == "ai":
            return str(message.get("content", ""))
    return ""


def _extract_history_messages(agent, thread_id, user_id):
    config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
    state = agent.get_state(config)
    values = getattr(state, "values", {}) if state is not None else {}
    raw_messages = values.get("messages", []) if isinstance(values, dict) else []

    history = []
    for message in raw_messages:
        message_type = getattr(message, "type", None)
        if message_type == "tool":
            continue
        if message_type not in {"human", "ai"}:
            if not isinstance(message, dict) or message.get("type") not in {"human", "ai"}:
                continue

        role = "user" if (message_type == "human" or (isinstance(message, dict) and message.get("type") == "human")) else "assistant"
        content = getattr(message, "content", "") if not isinstance(message, dict) else message.get("content", "")
        if isinstance(content, list):
            text = " ".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        else:
            text = str(content)
        history.append({"role": role, "content": text, "sources": []})
    return history


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app):
        checkpointer_cm, checkpointer = await open_checkpointer()
        repository = ConversationRepository()
        await repository.init_db()
        app.state.checkpointer_cm = checkpointer_cm
        app.state.checkpointer = checkpointer
        app.state.repository = repository
        app.state.agent = create_agent(checkpointer=checkpointer)
        yield
        await repository.close()
        await close_checkpointer(checkpointer_cm)

    app = FastAPI(title="AI Learning Assistant", lifespan=lifespan)

    web_dir = Path(__file__).resolve().parent.parent / "web"
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(web_dir / "index.html")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/conversations")
    async def create_conversation(payload: ConversationCreateRequest):
        user_id = _normalize_user_id(payload.user_id)
        thread_id = _normalize_thread_id(None)
        title = "新对话"
        await app.state.repository.create_conversation(user_id, thread_id, title)
        return {"thread_id": thread_id, "title": title}

    @app.get("/api/conversations")
    async def list_conversations(user_id: str = Query(...)):
        user_id = _normalize_user_id(user_id)
        rows = await app.state.repository.list_conversations(user_id)
        return [
            {
                "thread_id": row["thread_id"],
                "title": row["title"],
                "created_at": row.get("created_at"),
                "updated_at": row.get("updated_at"),
            }
            for row in rows
        ]

    @app.get("/api/conversations/{thread_id}/messages")
    async def get_conversation_messages(thread_id: str, user_id: str = Query(...)):
        user_id = _normalize_user_id(user_id)
        return _extract_history_messages(app.state.agent, thread_id, user_id)

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest) -> ChatResponse:
        user_id = _normalize_user_id(request.user_id)
        thread_id = _normalize_thread_id(request.thread_id)
        config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
        result = app.state.agent.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config,
        )

        answer = _extract_ai_answer(result.get("messages", []))
        await app.state.repository.update_conversation(user_id, thread_id, request.message)
        return ChatResponse(thread_id=thread_id, answer=answer, user_id=user_id)

    @app.post("/api/chat/stream")
    async def stream_chat(request: ChatRequest):
        user_id = _normalize_user_id(request.user_id)
        thread_id = _normalize_thread_id(request.thread_id)
        config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
        seen_sources = set()

        async def event_generator():
            nonlocal seen_sources
            try:
                await app.state.repository.update_conversation(user_id, thread_id, request.message)
                async for message_chunk, _metadata in app.state.agent.astream(
                    {"messages": [HumanMessage(content=request.message)]},
                    config=config,
                    stream_mode="messages",
                ):
                    message_type = getattr(message_chunk, "type", None)

                    if message_type == "tool":
                        for source_entry in _extract_tool_sources(message_chunk):
                            key = json.dumps(source_entry, sort_keys=True)
                            if key in seen_sources:
                                continue
                            seen_sources.add(key)
                            yield f"data: {json.dumps({'source': source_entry})}\n\n"
                        continue

                    if message_type == "ai" and isinstance(getattr(message_chunk, "content", ""), str):
                        content = message_chunk.content
                        if content:
                            payload = {"content": content}
                            yield f"data: {json.dumps(payload)}\n\n"
            except Exception as exc:  # minimal error handling only
                payload = {"error": str(exc)}
                yield f"data: {json.dumps(payload)}\n\n"
            finally:
                yield "data: {\"done\": true}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    return app


app = create_app()
