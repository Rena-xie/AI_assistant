# AI Learning Assistant


## Overview

AI Learning Assistant is a personal agent system designed to help learn and practice AI application engineering.


## Goals

Build an AI assistant with:

- Knowledge retrieval
- Document analysis
- AI engineering learning support
- Coding assistance
- Agent workflow


## Architecture

Current stage:

LLM + Agent framework

Implemented:

- Routing between chat and knowledge paths (`src/aila/graph/`)
- RAG knowledge retrieval (`src/aila/knowledge/`, `src/aila/rag/`)
- Short-term conversation memory (`src/aila/memory/`)
- Evaluation (`evals/`)

Future:

MCP + long-term memory


## Tech Stack

Python

LangChain

LangGraph

OpenAI-compatible APIs


## Development

Create environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configure environment variables (required):

```powershell
Copy-Item .env.example .env
# then edit .env and set OPENAI_API_KEY / OPENAI_BASE_URL / MODEL_NAME
```

`src/config.py` loads `.env` from the project root and fails fast with a clear
error message when a required variable is missing.

Run the assistant:

```powershell
python src/main.py
```

Type `exit` to quit the chat loop.

The assistant remembers the conversation while the process runs (LangGraph
`MemorySaver` checkpointer, one `thread_id` per chat window), so follow-up
questions keep their context. Restarting the assistant starts a new
conversation.
