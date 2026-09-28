import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import HumanMessage

from ..agent import create_agent
from .schemas import ChatRequest, ChatResponse


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


def create_app() -> FastAPI:
    app = FastAPI(title="AI Learning Assistant")
    agent = create_agent()

    web_dir = Path(__file__).resolve().parent.parent / "web"
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(web_dir / "index.html")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/chat", response_model=ChatResponse)
    def chat(request: ChatRequest) -> ChatResponse:
        config = {"configurable": {"thread_id": request.thread_id}}
        result = agent.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config,
        )

        answer = ""
        for message in reversed(result.get("messages", [])):
            if getattr(message, "type", None) == "ai":
                content = message.content
                if isinstance(content, list):
                    answer = " ".join(
                        part.get("text", "") if isinstance(part, dict) else str(part)
                        for part in content
                    )
                else:
                    answer = str(content)
                break

            if isinstance(message, dict) and message.get("type") == "ai":
                content = message.get("content", "")
                answer = str(content)
                break

        return ChatResponse(thread_id=request.thread_id, answer=answer)

    @app.post("/api/chat/stream")
    async def stream_chat(request: ChatRequest):
        config = {"configurable": {"thread_id": request.thread_id}}
        seen_sources = set()

        async def event_generator():
            nonlocal seen_sources
            try:
                async for message_chunk, _metadata in agent.astream(
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
