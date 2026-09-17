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


### Evaluation Layer

Responsible for:

- Agent quality evaluation
- Regression testing


## Engineering Principles


1. Everything should be reproducible

2. Every capability should have evaluation

3. Changes should be observable

4. Agents should modify code safely
