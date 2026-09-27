# System Architecture


## Overview

AI Learning Assistant is an agent-based application.


Architecture:


User

↓

Agent Runtime

↓

LLM

↓

Tools

↓

Knowledge


## Components


### Agent

Responsible for:

- Reasoning
- Tool selection
- Task execution


### Model Layer

Supports:

- OpenAI compatible APIs
- Multiple providers


### Knowledge Layer

Future:

- Vector database
- RAG pipeline


### Memory Layer

Responsible for:

- Short-term conversation memory (multi-turn context)

Stage 1 uses the official LangGraph ``MemorySaver`` checkpointer, wired in at
``graph.compile(checkpointer=get_checkpointer())``.

A conversation is identified by a ``thread_id``:

- one ``thread_id`` == one chat window
- it is **not** a user id — this is a single-user assistant,
  so there is no user system and no multi-user isolation
- checkpoints live in process memory only, so a restart starts a new
  conversation

Out of scope in stage 1: database persistence, user system, long-term
memory, vector-database memory and summarization / compression.


### Evaluation Layer

Responsible for:

- Agent quality evaluation
- Regression testing


## Engineering Principles


1. Everything should be reproducible

2. Every capability should have evaluation

3. Changes should be observable

4. Agents should modify code safely
