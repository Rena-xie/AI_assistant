### 第一阶段：AI辅助编程

目标：

熟悉：

```
VS Code
Cline
Git
Python
```

让 AI 帮你：

- 建项目结构
- 写 FastAPI
- 接 DeepSeek
- 写 RAG

---

### 第二阶段：Agent开发

加入：

```
LangChain
LlamaIndex
LangGraph
```

架构：

```
User
 |
 |
Agent
 |
 |---- LLM
 |
 |---- Tools
 |
 |---- Memory
 |
 |---- RAG
 |
Database
```

---

### 第三阶段：工程化

学习：

```
Docker
FastAPI
PostgreSQL
Vector DB
MCP
Evaluation
Deployment
```



06_ai_learning_assistant ├── .venv Python环境 ├── src 源代码 ├── docs 文档 ├── knowledge 知识库 ├── tests 测试 ├── evals Agent评估 ├── AGENTS.md Harness规则 ├── README.md └── .gitignore
python --version
py -0
node --version
npm --version
git --version









严格来说，**没有一个项目和你的想法 100% 一样**，因为你想做的是“个人 AI 工程师成长助手”，它融合了：

- AI tutor（学习助手）
- RAG knowledge base（知识库）
- Coding Agent（代码助手）
- MCP Agent（工具调用）
- Harness Engineering（Agent工程管理）

# 1. MemGPT / Letta —— 最接近“长期学习助手”的思想

项目：


[Letta GitHub](https://github.com/letta-ai/letta?utm_source=chatgpt.com)

它解决的问题：

> 如何让 Agent 拥有长期记忆？

架构思想：

```
User
 |
Agent
 |
Memory System
 |
Knowledge
 |
Tools
```

和你的想法对应：

你的：

```
学习进度
知识掌握情况
项目经验
踩坑记录
```

其实就是 Memory。

例如：

你问：

> 我现在应该学习什么？

Agent 不应该只看当前聊天。

它应该知道：

```
用户已经学习：
- Python
- RAG

正在学习：
- MCP
- Agent

薄弱：
- Evaluation
```

然后给建议。

---

你可以借鉴：

- memory设计
- persona设计
- agent state管理

---

# 2. OpenHands —— 最接近 Cline 的开源 Agent

项目：

OpenHands

GitHub：

[OpenHands GitHub](https://github.com/All-Hands-AI/OpenHands?utm_source=chatgpt.com)

它类似：

```
Cline
+
服务器化
+
Agent运行环境
```

能力：

- 写代码
- 修改项目
- 执行命令
- 浏览网页
- 调试

架构：

```
Agent

 |
Planner

 |
Executor

 |
Tools

 |
Environment
```

和你未来的 AI 学习助手非常接近。

因为你的助手以后可能也需要：

```
学习任务

↓

规划

↓

搜索资料

↓

总结

↓

生成代码实验

↓

验证
```

---

# 3. Khoj —— 很像“个人AI知识助手”

项目：

Khoj

GitHub：

[Khoj GitHub](https://github.com/khoj-ai/khoj?utm_source=chatgpt.com)

它主要做：

个人知识库 Agent：

```
Markdown
PDF
Notes
Emails
Documents

↓

Index

↓

RAG

↓

Chat
```

和你的：

```
AI知识库
官方文档
论文
学习笔记
```

高度类似。

你可以学习：

- 文档 ingestion
- embedding
- search
- personal knowledge graph

---

# 4. LlamaIndex —— 你的知识层应该参考它

项目：

LlamaIndex

GitHub：

[LlamaIndex GitHub](https://github.com/run-llama/llama_index?utm_source=chatgpt.com)

它不是完整 Agent，而是：

> 如何让 LLM 使用你的数据

你的：

```
官方文档

Github项目

论文

课程资料

笔记
```

都会进入：

```
Data Layer

↓

Retriever

↓

Agent
```

---

# 5. MCP Server项目 —— 你的“外部能力层”

你提到：

> 通过现有 MCP？

这是正确方向。

例如：

## GitHub MCP

让 Agent：

```
搜索repo

读取issue

查看代码
```

## Browser MCP

让 Agent：

```
搜索最新论文

读取官方文档
```

## Knowledge MCP

类似：

[Knowledge MCP Server GitHub](https://github.com/ximot/knowledge-mcp?utm_source=chatgpt.com)

架构：

```
Agent

↓

MCP

↓

Vector DB

↓

Knowledge
```

这与你未来设计非常类似。

---

# 6. Harness Engineering 项目参考

这里不是你的 AI 助手本身，而是参考“如何管理 Agent”。

比较值得看的：

## Lattice Harness Engineering

[Lattice Harness Engineering GitHub](https://github.com/lattice-technologies-inc/harness-engineering?utm_source=chatgpt.com)

它包含：

```
AGENTS.md

ARCHITECTURE.md

docs/

skills/

commands/
```

核心思想：

让 Agent 不靠聊天记忆，而靠仓库里的结构化知识工作。

这个和你现在设计：

```
06_ai_learning_assistant

├── AGENTS.md
├── docs/
├── knowledge/
├── skills/
├── evals/
```

非常接近。

---

# 如果我是你，我不会直接复制某一个项目

你的项目应该是一个“组合型项目”：

## 最终架构参考：

```
                  AI Learning Assistant


                         User

                          |
                          v

                  Agent Orchestrator

                          |

 ------------------------------------------------

 |                    |                         |

Memory              Knowledge                Tools

 |                    |                         |

Letta思想        LlamaIndex思想          MCP思想


                          |

                  Harness Layer

                          |

              AGENTS.md
              docs/
              skills/
              evals/
```





* **抓 Pattern（设计模式），忽略 Syntax（具体语法）**：注重架构逻辑与工程痛点，不死记硬背频繁废弃的 API 语法。
* **弃旧从新，查阅官网最新 API**：框架迭代极快，遇到报错立刻查阅官方最新 QuickStart 与 Cookbook。
* **核心竞争壁垒**：Evals（量化评估）、安全护栏（Prompt Injection 防护）、Token 降本与语义缓存机制。Ragas 评测指标的调优策略、Token 精细化管理及语义缓存机制的理解。包含如何量化 RAG 的召回率与准确率、如何防止 Prompt Injection（提示词注入）、如何做 Token 降本与 Context 缓存。

## 一、 技能体系总览

1. **第一层：编程语言与软件工程基础**
   包含 Python/TypeScript 核心语法、后端 REST API 开发、异步编程控制与容器化部署。
2. **第二层：大模型交互与 Prompt 工程**
   包含主流 LLM API/SDK 对接、高阶 Prompt 架构设计、Function Calling 参数解析与 Pydantic 结构化输出。
3. **第三层：RAG 检索增强与知识库**
   包含非结构化文档清洗切分、向量数据库与 Embedding 选型、混合检索（Dense+Sparse）与 Reranker 重排过滤。
4. **第四层：Agent 智能体编排与工作流**
   包含代码级框架（LangGraph、AutoGen、CrewAI）、MCP 开放协议以及低代码平台（Dify、n8n）的 POC 原型验证与二开。
5. **第五层：工程落地与 LLMOps 运维**
   包含全链路追踪（Tracing）、自动化评测（Evals）、安全防护（Guardrails）与高并发低延时性能调优。

## 二、 核心技能分类详解

### 1. 基础编程与软件工程 

* **核心语言掌握要求**
  * **Python（主流核心）**：掌握 List、Dict、Set 等高频数据结构，熟练运用条件分支与循环、文件 I/O、JSON 解析、面向对象基础（Class）；熟练进行 `.env` 环境变量读写与密钥隔离；能够清晰理清代码调用关系、看懂报错信息并具备编写与修改简单模块的能力。
  * **TypeScript / Node.js（全栈/UI 扩展）**：用于 Agent UI 交互界面开发或全栈 Web 应用构建。
* **后端框架与 API 交互**
  * **RESTful API 设计**：熟练使用 FastAPI（Python 主流）或 Express 框架，掌握路由管理、CORS 配置与 Pydantic v2 强类型声明。
  * **异步编程与高并发处理**：深入理解 Python `asyncio` 协程机制，熟练使用 `httpx.AsyncClient` 实现异步网络请求，有效降低高并发下的超长时延。
  * **流式传输**：掌握 SSE（Server-Sent Events）与 WebSocket 技术，实现打字机效果的高性能流式响应。
* **工程基本功与部署**
  * **工具链**：掌握 Git 团队协作、VS Code / Cursor 自动化工具以及 Terminal 命令行操作。
  * **数据与缓存**：配置 PostgreSQL 数据库与 Redis 缓存。
  * **容器化部署**：掌握 Docker 镜像打包，并部署至云服务器或 Vercel，配置 HTTPS。

### 2. 大模型交互与 Prompt 工程

* **大模型 API 与 SDK 集成**
  * 熟练对接 OpenAI、Anthropic、DeepSeek 等主流大模型 API 与 SDK。
  * 深入理解 Token 扣费物理机制、上下文窗口（Context Window）限制及 Embedding 原理。
* **提示词架构与优化**
  * **高阶 Prompt 设计**：熟练运用 System Prompt 角色设定、Few-Shot 少样本提示、CoT（思维链）等技术调优语义。
  * **强约束结构化输出**：结合 Pydantic / Instructor 实现大模型稳定输出 JSON Schema 格式数据，确保后端系统 100% 解析成功。
* **Function Calling（函数调用）**
  * 深刻理解 LLM 解析 JSON Schema 并生成工具调用参数的底层握手细节与参数提取。

### 3. RAG 检索增强生成技术栈

* **文档解析与文本切片 (Chunking)**
  * 处理 Markdown、复杂多栏 PDF 等非结构化文档，进行正则降噪与语义切片/重叠切片。
  * 理解 `RecursiveCharacterTextSplitter` 切分器的 Token 边界差异。
* **向量化与向量数据库**
  * 理解 Embedding 选型，熟练操作 Qdrant、Milvus、Chroma、Pinecone、PGVector 等向量数据库。
  * 掌握高性能元数据（Metadata）注入与元数据过滤（Metadata Filtering）。
* **检索优化与重排序**
  * **混合检索**：编写向量化检索（Dense）与关键词检索（Sparse / BM25）的双路召回代码。
  * **重排序（Reranking）**：配置 Reranker 模型进行过滤降噪，大幅提升检索精度。
  * **高级拓扑**：探索 GraphRAG 等图谱增强检索技术。

### 4. Agent 智能体编排与前沿协议

* **代码级编排框架**
  * **LangGraph**：主流循环/图结构编排框架，支持 State 状态持久化、Self-Correction 自动纠错循环与 Human-in-the-Loop 人工干预中断拦截。
  * **AutoGen / CrewAI**：多智能体协作与 SOP 任务分发框架。
  * **LlamaIndex / LangChain**：以数据与 RAG 为核心的 Agent 开发框架。
  * **核心范式**：掌握 ReAct 范式、Memory 动态记忆管理与多轮对话状态清洗。
* **前沿智能体协议**
  * **MCP（Model Context Protocol）**：攻坚开放的智能体上下文与工具接入协议落地。
* **低代码 / 可视化平台与二次开发**
  * **平台定位**：使用 Dify、Coze、n8n、FastGPT 快速构建 POC（概念验证原型）。
  * **代码扩展必要性**：面对复杂业务逻辑（Code 节点）、自定义工具/API 接口签名鉴权重试（Function Calling）、以及平台二次开发（私有化部署对接 SSO、修改数据库）时，必须依赖 Python 代码实现。

### 5. LLMOps、评估与工程安全性 (LLMOps, Evaluation & Safety)

* **全链路可观测性 (Tracing)**
  * 使用 LangSmith、Langfuse、Arize Phoenix 挂载全链路 Trace，追踪每次请求的节点耗时与 Token 消耗。
* **自动化评估评测 (Evals)**
  * 构建黄金评测集，利用 Ragas 等框架针对 RAG 的上下文检索、回答忠实度等四维度量化评测，监控工具调用准确率与幻觉率。
* **安全防护 (Guardrails)**
  * 部署提示词注入防护（Prompt Injection）、违规与敏感内容拦截防护网、工具调用权限管控与超时降级机制。
* **性能与延时优化**
  * 结合异步编程（httpx/FastAPI）、语义缓存（Semantic Cache）与模型分流路由，将百级并发下的响应延时控制在 500ms 内。

## 三、 落地 6 大核心工作流

1. **业务拆解与架构设计**：精准评估 AI 引入必要性，合理区分规则代码（If/Else/SQL/正则）与 LLM 职责界限，混用大中小模型控制并发与成本。
2. **RAG 数据管道构建**：多格式文档清洗切分 -> 高质量元数据注入 -> 向量/关键词双路召回 -> Reranker 过滤降噪 -> 大模型高精度回答。
3. **提示词设计与强约束结构化输出**：Few-Shot/COT 结合 Pydantic 强制输出 JSON Schema，确保后端无缝解析。
4. **Agent 工具扩展与外部系统对接**：编写标准 Python 工具函数，对接企业 ERP/CRM/数据库，实现签名鉴权、接口重试与平滑熔断降级。
5. **工程化服务交付**：利用 FastAPI asyncio 异步接口，配合 SSE（Server-Sent Events）实现打字机流式响应，利用 Docker 容器化打包部署。
6. **全链路评估与 LLMOps 监控**：Langsmith/Langfuse 耗时与 Token 监控 + Ragas 评测集量化迭代，确保系统无性能倒退。

## 四、 4 阶段递进学习路线

1. **第一阶段：跑通 Hello-World 与基础 API**
   阅读核心教程，直接使用 Python 手写简单 ReAct Agent（不依赖框架，使用 OpenAI API 与原生函数）。
2. **第二阶段：掌握 RAG 与工具链**
   结合 Chroma 向量数据库搭建知识库问答 Agent，并扩展网络搜索（Tavily）、代码执行器及数据库工具。
3. **第三阶段：深入框架与复杂工作流**
   深入学习 LangGraph 编写支持“反思-重试-人工干预”的循环控制流 Agent，并实践 MCP 协议工具接入。
4. **第四阶段：项目实战与工程化落地**
   开发完整 Agent 产品，配置前端界面与 SSE 流式响应，部署至 Docker，并接入 LangSmith 进行全链路 Trace 与评测调试。

