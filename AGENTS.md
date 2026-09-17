# AGENTS.md

## Project Overview

This project is an AI Learning Assistant.

The goal is to build a personal AI assistant that helps users learn AI application engineering.

The assistant should support:

- AI knowledge learning
- Document understanding
- Latest AI information retrieval
- Coding assistance
- Agent workflow experimentation


## Engineering Principles

Follow these principles:

1. Keep the architecture simple.
2. Prefer modular design.
3. Write readable Python code.
4. Document important decisions.
5. Add evaluation cases for AI behaviors.


## Technology Stack

Current stack:

- Python 3.13
- LangChain
- LangGraph
- OpenAI-compatible API
- MCP (future)
- RAG (future)


## Code Rules

When modifying code:

- Explain the purpose before major changes.
- Avoid unnecessary dependencies.
- Keep functions small.
- Add comments for complex logic.


## Project Structure

src/
    Application source code

docs/
    Design documents

knowledge/
    Knowledge base resources

tests/
    Software tests

evals/
    Agent evaluation cases


## Development Workflow

Before implementing features:

1. Read relevant documents.
2. Understand existing architecture.
3. Propose changes.
4. Implement.
5. Test.
6. Update documentation.