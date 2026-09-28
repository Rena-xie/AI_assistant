# AI Learning Assistant — Curriculum

## 1. Curriculum Purpose

本课程体系用于定义 AI 应用开发工程师所需的长期能力地图。

它不是简单的技术清单，也不是要求用户按固定顺序学完所有框架。

Agent 应根据：

* 当前目标；
* 当前能力；
* 前置能力；
* 当前项目；
* 实践证据；
* 评估结果；

动态决定用户当前应该学习和练习什么。

课程体系的基本结构：

```text
Capability
↓
Knowledge
↓
Tool / Framework
↓
Practice
↓
Project
↓
Evidence
↓
Mastery
```

---

# 2. Mastery Levels

所有核心能力统一使用以下六级能力等级。

### L0 — Unknown

尚未接触，无法解释基本概念。

### L1 — Explain

能够：

* 解释基本概念；
* 说明用途；
* 识别基本组成部分；
* 阅读简单示例。

不能稳定完成实际任务。

### L2 — Use

能够：

* 按已有示例完成基本使用；
* 调用 API；
* 使用框架已有功能；
* 完成简单练习。

遇到变化较大的问题仍需要指导。

### L3 — Modify / Debug

能够：

* 修改已有代码；
* 排查常见错误；
* 根据需求调整配置；
* 理解代码调用关系；
* 将一个示例改造成相似场景。

### L4 — Design / Evaluate

能够：

* 独立设计解决方案；
* 进行技术选型；
* 比较不同方案；
* 设计测试与评测；
* 分析系统问题；
* 解释技术取舍。

### L5 — Independently Deliver

能够独立完成真实 AI 应用中的一个完整能力模块或小型系统：

```text
需求
→ 设计
→ 实现
→ 调试
→ 测试
→ 评估
→ 部署
→ 迭代
```

---

# 3. Capability Map

课程分为十二个能力域。

```text
C1 编程与软件工程
C2 LLM 应用开发
C3 Prompt 与结构化输出
C4 RAG
C5 Agent Engineering
C6 Backend & API
C7 Evaluation
C8 Observability & LLMOps
C9 Security & Reliability
C10 Deployment & Performance
C11 AI Application System Design
C12 Engineering Workflow & Harness Engineering
```

其中：

### Core

必须形成较强能力：

```text
C1 C2 C4 C5 C6 C7 C11 C12
```

### Supporting

需要达到能够实际使用和解决问题的程度：

```text
C3 C8 C9 C10
```

具体工具不需要全部达到 L5。

---

# 4. C1 — Programming & Software Engineering

## C1.1 Python Fundamentals

### Knowledge

* 变量
* List
* Dict
* Set
* Tuple
* 条件分支
* 循环
* 函数
* 参数
* return
* 异常
* Module
* Package
* Class / Object
* 文件 I/O
* JSON
* 类型提示
* 环境变量
* `.env`
* 基本依赖管理

### Tools

* Python
* VS Code
* Terminal
* Git

### Practice

* 修改简单 Python 模块；
* 读取 JSON；
* 调用 API；
* 编写简单工具函数；
* 根据报错定位问题；
* 阅读已有 AI 应用代码。

### Evidence

* 独立修改一个简单模块；
* 能解释函数调用关系；
* 能根据 traceback 定位基本错误；
* 能完成简单数据处理任务。

### Mastery

最低目标：

```text
Python Core → L3
```

不要求成为专业 Python 软件工程师。

---

## C1.2 Git & Engineering Workflow

### Knowledge

* repository
* commit
* branch
* merge
* diff
* status
* pull
* push
* .gitignore
* GitHub

### Practice

* 创建项目仓库；
* 提交代码；
* 查看 diff；
* 回退错误修改；
* 使用 branch 完成功能开发。

### Evidence

能够独立维护自己的 AI 项目 Git 仓库。

### Mastery

```text
L3
```

---

## C1.3 TypeScript / Node.js

### Purpose

作为 AI 应用前端和全栈扩展能力。

### Knowledge

* TypeScript 基础语法
* npm
* Node.js
* async / await
* API 调用
* 前端状态管理基础

### Tools

* TypeScript
* Node.js

### Mastery

```text
L1 → L2
```

先达到能够阅读和修改 AI 应用前端代码的程度。

---

# 5. C2 — LLM Application Development

## C2.1 LLM API

### Knowledge

* Chat API
* messages
* system / user / assistant
* temperature
* token
* context window
* streaming
* structured output
* model selection
* error handling

### Tools

至少掌握一种主流 LLM API。

同时理解：

```text
模型能力
API 能力
应用层能力
```

三者的区别。

### Practice

* 原生 API 调用；
* Streaming；
* 多轮上下文；
* API 错误处理；
* 模型切换。

### Evidence

能够不依赖低代码平台直接调用 LLM 完成一个简单应用。

### Mastery

```text
L3
```

---

## C2.2 Token & Context Engineering

### Knowledge

* Token
* Context Window
* Context Compression
* Context Selection
* Prompt 长度
* 历史消息管理
* Context Pollution

### Practice

分析一个 Agent 为什么：

* 越聊越慢；
* 上下文越来越长；
* 记忆污染当前问题；
* 检索内容干扰模型判断。

### Mastery

```text
L3
```

---

# 6. C3 — Prompt & Structured Output

## C3.1 Prompt Architecture

### Knowledge

* System Prompt
* User Prompt
* Instruction hierarchy
* Few-shot
* Output constraints
* Task decomposition
* Prompt templates
* Context injection

### Principle

Prompt 不是单纯“写得更漂亮”，而是应用系统中的控制接口。

### Practice

* 为 Agent 编写 system prompt；
* 为不同任务设计 prompt；
* 比较不同 Prompt 版本；
* 设计失败案例。

### Evidence

能够解释 Prompt 中每个关键规则为什么存在。

### Mastery

```text
L3 → L4
```

---

## C3.2 Structured Output

### Knowledge

* JSON
* JSON Schema
* Pydantic
* schema validation
* parsing
* retry / repair

### Practice

让模型输出：

```text
计划
任务
评估结果
工具参数
结构化报告
```

### Mastery

```text
L3
```

---

## C3.3 Tool Calling

### Knowledge

* Tool
* Tool schema
* arguments
* tool result
* tool loop
* validation
* permission
* retry
* timeout

### Practice

实现：

```text
LLM
→ tool call
→ tool execution
→ tool result
→ LLM
```

### Mastery

```text
L3 → L4
```

---

# 7. C4 — RAG

## C4.1 RAG Fundamentals

### Knowledge

```text
Document
→ Parsing
→ Cleaning
→ Chunking
→ Embedding
→ Index
→ Retrieval
→ Reranking
→ Generation
```

理解：

* 为什么需要 RAG；
* RAG 的适用场景；
* RAG 和 Fine-tuning 的区别。

### Mastery

```text
L3
```

---

## C4.2 Document Processing

### Knowledge

* Markdown
* TXT
* PDF
* HTML
* Metadata
* Cleaning
* Chunking
* overlap
* semantic chunking

### Tools

至少掌握一种文档处理方案。

例如：

* Docling
* Marker
* MinerU

不要求全部掌握。

### Practice

建立：

```text
Raw documents
→ Cleaned Markdown
→ Structured documents
```

### Mastery

```text
L3
```

---

## C4.3 Embedding & Vector Database

### Knowledge

* Embedding
* similarity
* cosine similarity
* vector index
* metadata filtering

### Tools

至少实际使用一种：

* Chroma
* Qdrant
* PGVector
* Milvus
* Pinecone

### Mastery

```text
L3
```

---

## C4.4 Retrieval

### Knowledge

* Dense Retrieval
* Sparse Retrieval
* BM25
* Hybrid Retrieval
* Top-K
* Filtering
* Reranking

### Practice

对比：

```text
Dense
vs
Sparse
vs
Hybrid
vs
Hybrid + Reranker
```

### Mastery

```text
L3 → L4
```

---

## C4.5 RAG Evaluation

### Knowledge

* Recall
* Precision
* Hit Rate
* MRR
* NDCG
* Faithfulness
* Answer Relevance

### Practice

建立黄金测试集并比较不同 RAG 方案。

### Mastery

```text
L4
```

---

# 8. C5 — Agent Engineering

## C5.1 Agent Fundamentals

### Knowledge

理解：

* Agent
* Tool
* State
* Memory
* Planning
* Routing
* Workflow
* Loop
* Human-in-the-Loop

### Mastery

```text
L3
```

---

## C5.2 ReAct

### Knowledge

```text
Reason / Decide
↓
Action
↓
Observation
↓
Continue
```

理解 Tool Calling 与 ReAct 的关系。

### Practice

使用原生 Python + LLM API 实现简单 Agent。

### Mastery

```text
L3
```

---

## C5.3 LangGraph

### Knowledge

* State
* Node
* Edge
* Conditional Edge
* Checkpoint
* Persistence
* Interrupt
* Human-in-the-Loop
* Loop

### Practice

构建：

* Router Agent
* Tool Agent
* RAG Agent
* Reflection / Retry Workflow
* Human approval workflow

### Mastery

```text
L3 → L4
```

---

## C5.4 Agent Memory

### Knowledge

区分：

```text
Conversation History
Long-term User Memory
Learning State
Working State
```

理解不同状态为什么不能全部混在聊天记录中。

### Mastery

```text
L4
```

---

## C5.5 Multi-Agent

### Knowledge

* Supervisor
* Worker
* Delegation
* Role separation
* Shared state
* Communication

### Tools

* LangGraph
* AutoGen
* CrewAI

### Mastery

以理解适用场景为主：

```text
L2 → L3
```

不要求同时熟练掌握多个框架。

---

## C5.6 MCP

### Knowledge

* MCP Client
* MCP Server
* Tool
* Resource
* Prompt
* Context

### Practice

完成一个 MCP Server / Client 工具接入。

### Mastery

```text
L2 → L3
```

---

## C5.7 Low-code Agent Platforms

### Platforms

* Dify
* Coze
* n8n
* FastGPT

### Purpose

主要用于：

* POC
* 快速验证
* 工作流原型
* 对比平台能力
* 企业场景快速交付

### Mastery

至少一个平台：

```text
L3
```

其他平台：

```text
L1 → L2
```

---

# 9. C6 — Backend & API Engineering

## C6.1 HTTP & REST

### Knowledge

* HTTP
* GET
* POST
* PUT
* DELETE
* headers
* status code
* JSON
* REST API

### Mastery

```text
L3
```

---

## C6.2 FastAPI

### Knowledge

* route
* request
* response
* Pydantic
* dependency
* middleware
* CORS
* error handling

### Practice

构建 AI API：

```text
POST /chat
POST /chat/stream
GET /health
```

### Mastery

```text
L3 → L4
```

---

## C6.3 Async Programming

### Knowledge

* coroutine
* async
* await
* event loop
* concurrency
* blocking vs non-blocking
* `httpx.AsyncClient`

### Mastery

```text
L3
```

---

## C6.4 Streaming

### Knowledge

* SSE
* WebSocket
* streaming response
* buffering
* event parsing

### Mastery

```text
L3
```

---

# 10. C7 — Evaluation

## C7.1 Evaluation Fundamentals

### Knowledge

理解：

```text
Test
vs
Evaluation
vs
Monitoring
```

### Principle

AI 系统不能只通过人工主观体验判断。

---

## C7.2 Golden Dataset

### Knowledge

* test cases
* expected behavior
* reference answer
* retrieval relevance
* tool-call expectation

### Practice

建立一个小型黄金评测集。

### Mastery

```text
L3 → L4
```

---

## C7.3 RAG Evaluation

至少掌握：

* Recall
* Precision
* Hit Rate
* MRR / NDCG
* Faithfulness
* Relevance

### Mastery

```text
L4
```

---

## C7.4 Agent Evaluation

### Knowledge

评估：

* route accuracy
* tool selection
* tool arguments
* final answer
* failure recovery
* state transitions

### Mastery

```text
L4
```

---

# 11. C8 — Observability & LLMOps

## C8.1 Tracing

### Tools

* LangSmith
* Langfuse
* Arize Phoenix

至少实际使用一种。

### Knowledge

能够查看：

```text
Request
→ LLM
→ Tool
→ Retrieval
→ Node
→ Final Answer
```

### Mastery

```text
L3
```

---

## C8.2 Metrics

关注：

* Latency
* Token usage
* Cost
* Error rate
* Tool success rate
* Retrieval metrics
* Evaluation score

### Mastery

```text
L3
```

---

# 12. C9 — Security & Reliability

## C9.1 AI Security

### Knowledge

* Prompt Injection
* Data Leakage
* Tool Abuse
* Permission Control
* Secret Management

### Practice

模拟攻击：

```text
User
→ Prompt Injection
→ Agent
→ Tool
```

验证系统是否能够限制危险操作。

### Mastery

```text
L3
```

---

## C9.2 Reliability

### Knowledge

* timeout
* retry
* fallback
* rate limit
* circuit breaker
* graceful degradation
* validation

### Mastery

```text
L3
```

---

# 13. C10 — Deployment & Performance

## C10.1 Database

### Knowledge

* SQL
* relational database
* PostgreSQL
* schema
* index
* transaction

### Mastery

```text
L2 → L3
```

---

## C10.2 Redis

### Knowledge

* cache
* key-value
* TTL
* session
* rate limiting

### Mastery

```text
L1 → L2
```

---

## C10.3 Docker

### Knowledge

* image
* container
* Dockerfile
* compose
* environment variables
* volume
* network

### Practice

将 AI 应用容器化。

### Mastery

```text
L3
```

---

## C10.4 Deployment

理解：

```text
Local
→ Server
→ HTTPS
→ Domain
→ Monitoring
```

能够完成至少一次完整部署。

### Mastery

```text
L3
```

---

## C10.5 Performance

### Knowledge

* latency
* throughput
* concurrency
* batching
* caching
* model routing
* async I/O

重点不是死记一个固定性能指标，而是能够定位性能瓶颈并进行优化。

### Mastery

```text
L3
```

---

# 14. C11 — AI Application System Design

这是整个课程体系中非常重要的能力。

## C11.1 AI Problem Decomposition

能够判断：

```text
Rule
vs
Code
vs
LLM
vs
RAG
vs
Agent
```

### Mastery

```text
L4
```

---

## C11.2 Architecture Design

能够设计：

```text
Frontend
↓
API
↓
Agent
↓
Tools / RAG
↓
Models
↓
Storage
↓
Evaluation
↓
Observability
```

### Practice

为一个 AI 产品输出：

* architecture diagram
* API design
* data flow
* state model
* error handling
* evaluation plan

### Mastery

```text
L4
```

---

## C11.3 Technology Selection

能够解释为什么选择：

* 某个模型；
* 某个数据库；
* 某个 Agent framework；
* 某种 RAG strategy；
* 某种部署方式。

不能只回答：

> “因为它比较流行。”

### Mastery

```text
L4
```

---

# 15. C12 — Engineering Workflow & Harness Engineering

## C12.1 AI-assisted Development

### Knowledge

* AI coding assistant
* repository context
* task specification
* implementation plan
* verification
* iterative debugging

### Tools

* VS Code
* Cursor
* Cline
* GitHub Copilot

### Mastery

```text
L3
```

---

## C12.2 Harness Engineering

核心能力：

```text
Mission
↓
Specifications
↓
Tools
↓
Constraints
↓
State
↓
Evaluation
↓
Feedback Loop
```

用户需要理解：

> 高质量 AI 应用不是只靠更强模型，而是通过工程系统约束模型行为。

### Practice

为 Agent 建立：

* system instructions
* tool contracts
* state model
* evaluation set
* guardrails
* failure handling

### Mastery

```text
L4
```

---

# 16. Capability Dependencies

部分能力存在明显前置关系。

```text
Python
↓
API / Backend
↓
LLM API
↓
Tool Calling
↓
Agent
↓
LangGraph
↓
Complex Workflow
```

RAG：

```text
Python
↓
Document Processing
↓
Embedding
↓
Vector DB
↓
Retrieval
↓
Reranking
↓
RAG Evaluation
```

工程化：

```text
Python
↓
FastAPI
↓
Async
↓
Streaming
↓
Docker
↓
Deployment
```

LLMOps：

```text
LLM / Agent
↓
Tracing
↓
Evaluation
↓
Safety
↓
Performance
```

系统设计：

```text
基础能力
+
LLM
+
RAG
+
Agent
+
Backend
+
Evaluation
↓
AI Application System Design
```

---

# 17. Recommended Learning Stages

课程不是严格锁死的，但默认路线如下。

## Stage 1 — Foundation

重点：

```text
Python
Git
HTTP
LLM API
Prompt
Tool Calling
```

目标：

能够不依赖低代码平台完成简单 AI 应用。

---

## Stage 2 — RAG & Tools

重点：

```text
Document Processing
Embedding
Vector DB
Retrieval
Reranker
Web Search
Tools
```

目标：

能够完成具备知识库和外部工具的 AI 应用。

---

## Stage 3 — Agent Engineering

重点：

```text
ReAct
State
Memory
Routing
LangGraph
MCP
Human-in-the-Loop
```

目标：

能够设计复杂 Agent 工作流。

---

## Stage 4 — Engineering

重点：

```text
FastAPI
Async
SSE
Database
Docker
Deployment
```

目标：

能够把 Agent 做成可以运行的应用服务。

---

## Stage 5 — Evaluation & LLMOps

重点：

```text
Golden Dataset
RAG Evaluation
Agent Evaluation
Tracing
Security
Reliability
Performance
```

目标：

能够判断系统是否可靠，并能够持续迭代。

---

## Stage 6 — System Design & Independent Delivery

最终重点：

```text
Problem Decomposition
+
Architecture
+
Implementation
+
Evaluation
+
Deployment
+
Iteration
```

目标：

独立完成一个完整 AI 应用项目。

---

# 18. Project-Based Learning

课程不应完全按照“学完一个知识点再学下一个知识点”的方式进行。

每个重要能力应尽可能绑定实践项目。

推荐项目递进：

### Project 1 — LLM API Application

练习：

* Python
* API
* Prompt
* structured output

### Project 2 — RAG Knowledge Assistant

练习：

* document processing
* embedding
* vector DB
* retrieval
* evaluation

### Project 3 — Tool-using Agent

练习：

* tool calling
* ReAct
* web search
* state

### Project 4 — LangGraph Agent

练习：

* routing
* persistence
* memory
* workflow
* human-in-the-loop

### Project 5 — Production-style AI Application

练习：

```text
Frontend
+
FastAPI
+
Agent
+
RAG
+
Tools
+
Streaming
+
Evaluation
+
Tracing
+
Docker
+
Deployment
```

### Project 6 — AI Learning Assistant

当前项目本身作为最终综合项目。

它用于验证：

* Agent Engineering
* Memory
* State
* Planning
* Evaluation
* RAG
* Web Search
* Backend
* Streaming
* Observability
* Harness Engineering

---

# 19. Evidence Model

每项能力都应该逐渐形成证据。

证据类型包括：

```text
Explanation
Practice
Code
Debugging
Test
Evaluation
Project
Design
Deployment
```

证据强度原则：

```text
“我学过”
<
“我能解释”
<
“我能使用”
<
“我能修改”
<
“我能调试”
<
“我能设计”
<
“我能独立完成”
```

Agent 不应因为用户回答正确一次，就永久认为能力已经掌握。

应结合多个证据判断。

---

# 20. Mastery Rules

### Rule 1

课程完成度不等于能力完成度。

### Rule 2

单纯阅读教程不能直接将能力提升到 L3 以上。

### Rule 3

L4 以上必须存在设计、评测或问题解决证据。

### Rule 4

L5 必须存在真实项目交付证据。

### Rule 5

能力状态应允许下降。

如果长期没有使用，或新的任务暴露明显问题，Agent 可以重新评估该能力等级。

---

# 21. Curriculum Evolution

课程体系需要长期维护。

新技术出现时，Agent 应首先判断：

```text
它解决什么问题？
↓
属于哪个能力域？
↓
是否改变已有工程范式？
↓
是否值得加入主线？
↓
需要达到什么掌握等级？
```

新技术不应因为热门而直接成为新的学习主线。

模型、框架和工具会变化，因此课程的长期核心应保持在：

```text
Problem Solving
+
Engineering
+
LLM Application
+
RAG
+
Agent
+
Evaluation
+
System Design
```

而具体工具属于可替换实现。

---

# 22. Curriculum Completion

课程不以“全部知识点学完”为终点。

真正的完成标准是：

用户能够独立完成一个具有实际复杂度的 AI 应用，并能够：

1. 分析需求；
2. 设计架构；
3. 选择模型和技术；
4. 编写和修改代码；
5. 接入 RAG / Tools / Agent；
6. 调试系统；
7. 建立评测；
8. 分析运行链路；
9. 完成部署；
10. 根据评测结果持续迭代。

最终目标：

> **从“学习 AI 应用开发”转变为“能够独立完成 AI 应用工程”。**
