from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    thread_id: str | None = None
    user_id: str | None = None


class ChatResponse(BaseModel):
    thread_id: str
    answer: str
    user_id: str | None = None


class ConversationCreateRequest(BaseModel):
    user_id: str | None = None


class ConversationMeta(BaseModel):
    thread_id: str
    title: str
    created_at: str | None = None
    updated_at: str | None = None


class ConversationHistoryEntry(BaseModel):
    role: str
    content: str
    sources: list[dict] | None = None
