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

Future:

RAG + Memory + MCP + Evaluation


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
