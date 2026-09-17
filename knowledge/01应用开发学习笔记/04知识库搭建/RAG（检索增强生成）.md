## 一、 RAG 的核心定义与解决痛点

### 1. 什么是 RAG？
* **全称**：Retrieval-Augmented Generation（检索增强生成）。
* **核心逻辑**：在将问题提交给大语言模型（LLM）之前，先从私有知识库或外部数据源中检索出高相关性的文本片段，将这些片段作为上下文信息（Context）补充到 Prompt 中，引导大模型基于事实依据生成准确回答。
* **典型应用场景**：企业私有知识库问答、智能客服系统、专业领域文档检索助手。

### 2. 为什么需要 RAG？（直连大模型的三大瓶颈）
如果直接将几百/上千页的文档与用户提问打包发送给大模型，会遇到以下突出问题：
* **上下文窗口限制（Context Window Limit）**：模型输入 token 存在上限，超长输入易导致信息遗忘（“中间遗忘”现象）或推理能力下降。
* **推理成本高昂（High Cost）**：大模型 API 计费直接与输入 Token 数挂钩，每次提问都附带全量文档成本不可接受。
* **推理延迟变大（Slow Speed）**：输入 Token 暴增会显著延长模型的首字响应时间（TTFT）和生成延迟。

RAG 通过“先精准检索少量核心片段，再提交生成”的方式，实现了低成本、低延迟与高准确率的统一。

## 二、 经典 RAG 两大阶段与五大核心环节

RAG 的工作流分为提问前的知识库构建阶段与提问后的实时响应阶段。

### 1. 提问前：数据准备阶段
* **分片（Chunking）**：将海量长文档拆分为独立、语义完整的文本块。策略包括按固定字符数、按段落、按章节或按语义切分。
* **索引（Indexing）**：利用 Embedding 模型将文本片段转换为高维语义向量，并将“原始文本”与“对应向量”同步保存至向量数据库（如 Chroma DB）。
  * **Embedding 模型**：将语义相近的文本映射到高维空间中邻近的向量（如 768 维）。
  * **向量数据库**：同时存储向量与原始文本，向量用于极速相似度比对，原始文本才是最终提交给大模型的真实输入。

### 2. 提问后：回答生成阶段
* **召回（Recall / Retrieval）**：将用户输入的问题转化为向量，在向量数据库中进行相似度计算，提取 Top-K（如 Top 5/10）相似片段。常用比对方法包括余弦相似度（Cosine Similarity）、欧氏距离（Euclidean Distance）与点积（Dot Product）。
* **重排（Reranking）**：使用高精度 Cross-Encoder（交叉编码器）模型对召回的候选片段进行二元联合打分与倒序精筛，提炼出相关度最高且噪音最低的 Top-N（如 Top 3）片段。
  * **“召回 + 重排”双阶段必要性**：向量召回（粗筛）计算极快但精度略低；Cross-Encoder 重排（精筛）精度极高但计算量大。双阶段协同兼顾了速度与精准度。
* **生成（Generation）**：将用户问题与重排提炼出的上下文片段拼接构造 Prompt，送入生成大模型（如 Gemini 2.5 Flash），输出基于事实的最终回答。

## 三、 RAG 架构的三大演进阶段

RAG 技术架构经历了从简单线性流水线到高度解耦模块化的演化：

### 1. 朴素 RAG（Naive RAG）
采用简单的“索引 -> 检索 -> 生成”单向线性流水线。缺点是容易遇到检索不精准、上下文冗余或检索结果无法回答问题等瓶颈。

### 2. 高级 RAG（Advanced RAG）
在朴素 RAG 基础上引入了检索前与检索后处理机制：
* **检索前处理**：包含查询重写（Query Rewrite）、假设性文档嵌入（HyDE）等，优化用户意图表达。
* **检索后处理**：引入重排序（Rerank）与上下文重过滤（Filter），精炼召回内容。

### 3. 模块化 RAG（Modular RAG）
解耦传统固定流向，拆解为高度独立、自由组合的六大功能模块以及底层的控制调度系统。

## 四、 模块化 RAG 核心模块与控制编排

### 1. 索引模块（Indexing）
* **切分优化**：采用“小块检索大块输出”（Small-to-Big），匹配时使用句子级小切片保证精度，输出时提取对应的完整段落或上下文。
* **结构化组织**：构建层级索引结构（树状层级）或引入知识图谱（Knowledge Graph），提取实体与三元组关系。

### 2. 检索前模块（Pre-Retrieval）
* **查询转换**：HyDE（通过生成假设回答进行检索）、反向 HyDE。
* **查询扩展**：子查询拆解（Sub-Query）、验证链（Verification Chain）。
* **查询构建**：Text-to-Cypher / Text-to-SQL，将自然语言转化为数据库专业查询。

### 3. 检索模块（Retrieval）
* **检索器微调**：利用 LM-Supervised 正负样本对比学习，对检索模型进行针对性微调。
* **混合检索（Hybrid Retrieval）**：将基于 Embedding 的稠密向量检索与基于关键词（BM25/TF-IDF）的稀疏检索结合，兼顾语义泛化与精确匹配。

### 4. 检索后模块（Post-Retrieval）
* **多类型重排**：使用 Cross-Encoder 对文本块、代码、表格等多源异构数据联合打分。
* **上下文压缩**：使用 LLM Lingua 等工具进行 Token 级长文本压缩，或利用 LLM 智能挑选最核心内容。

### 5. 生成与验证模块（Generation & Verification）
* **生成器微调**：对大模型进行专有上下文遵循能力微调。
* **结果质检与闭环**：包含幻觉检测（Hallucination Detection）、回答完整度评估、审查模型及隐私数据过滤。检测通过则输出答案，有瑕疵则触发二次检索（Do RAG Again），无条件回答则拒绝回答。

### 6. 控制与调度编排（Orchestration）
* **智能路由（Routing）**：分析 Query 意图，区分仅依赖检索文本的硬提示管线（Hard Prompt Pipeline）与允许结合模型内生知识的软提示管线（Soft Prompt Pipeline）。
* **循环调度（Scheduling）**：建立包含“是否需要检索”、“答案评估与重新检索”的分支闭环控制。
* **知识引导（Knowledge Guide）**：基于知识图谱规划推理路径（Reasoning Path），引导检索与生成交替推进。

### 1. 环境搭建与依赖安装
项目使用 `uv` 进行高效依赖与虚拟环境管理，推荐启动 Jupyter Notebook 进行调试：

```bash
# 初始化项目
mkdir rag && cd rag
uv init .
rm main.py

# 安装核心依赖库
uv add sentence-transformers chromadb google-genai python-dotenv

# 启动 Jupyter Notebook
uv run jupyter notebook
```

**核心依赖库作用**：
* `sentence-transformers`：加载 Embedding 模型与 Cross-Encoder 重排模型。
* `chromadb`：轻量级向量数据库，存储向量与文本片段并执行相似度比对。
* `google-genai`：官方 SDK，用于调用 Gemini 2.5 Flash 生成最终回答。
* `python-dotenv`：读取 `.env` 配置文件中的环境变量（如 `GEMINI_API_KEY`）。




# 用Python实现RAG系统 —— 学习笔记

## 一、RAG整体流程

分为两大部分：

**1. 用户提问前（数据准备）**

- 分片（Chunking）
- 索引（Indexing）

**2. 用户提问后（问答）**

- 召回（Retrieve）
- 重排（Rerank）
- 生成（Generate）

流程串联：文档 → 分片 → 向量化 → 存入向量数据库（准备完毕）；用户提问 → 问题向量化 → 向量数据库召回top10相关片段 → cross-encoder重排取top3 → 连同问题一起交给大模型生成答案。

---

## 二、环境准备

**所需工具：**

- `uv`：Python包管理器，管理依赖
- Jupyter Notebook：交互式代码执行环境，便于逐段调试

**初始化项目：**

```
uv init rag
```

执行后目录会生成三个文件：

- `main.py`（默认生成，用不到，因为用notebook写代码，可删除）
- `pyproject.toml`（存储项目元信息和依赖列表）
- `README.md`

**安装依赖及各自用途：**

|依赖|用途|
|---|---|
|sentence-transformers|加载embedding模型和cross-encoder模型|
|chromadb|向量数据库|
|google-genai|调用Gemini模型生成答案（用的是gemini-2.5-flash）|
|python-dotenv|把`.env`中的API Key读取为环境变量|

**启动Jupyter Notebook：** 不能用普通方式打开（否则读不到uv装的依赖），要用：

```
uv run jupyter notebook
```

**准备测试文档：** 找一篇模型训练数据中大概率没见过的文章放入项目目录，作为知识库源文件（用于验证RAG确实是基于文档内容回答，而非模型自身知识）。

---

## 三、分片 Chunking

- 定义函数 `split_into_chunks(doc_path) -> List[str]`
- 内部逻辑：读取文件内容 → 按行切分成多个chunk，返回chunk列表

---

## 四、索引 Indexing

### 1. 生成向量（Embedding）

- 引入 `SentenceTransformer`，加载一个embedding模型
- 定义函数 `embed_chunk(chunk) -> List[float]`：调用embedding模型，返回该片段对应的向量（本例中为768维）
- 循环对所有chunk调用该函数，得到全部片段的向量列表
- **注意**：首次运行会从HuggingFace下载模型（约400MB左右），需保持网络畅通，之后运行会很快

### 2. 存入向量数据库

- 使用 **ChromaDB**
- 创建客户端两种方式：
    - `chromadb.EphemeralClient()`：内存型客户端，数据不落盘，程序结束即清空
    - `chromadb.PersistentClient(path="...")`：持久化到磁盘指定文件/目录
- 创建一个 collection（类似传统数据库中的"表"）
- 写入函数：参数为 `chunks`（片段内容列表）和 `embeddings`（对应向量列表），长度需一致
    - 内部需生成 `ids`（如 "0" ~ "9" 的字符串列表，ChromaDB要求每条记录都有唯一ID）
    - 调用collection的写入方法，把chunks、embeddings、ids一起传入
- **踩坑提示**：执行时可能输出若干报错信息，通常是ChromaDB与其他依赖版本不完全兼容导致，不影响实际使用

---

## 五、召回 Retrieve

- 定义函数 `retrieve(query, top_k) -> List[str]`
- 参数：`query`（用户问题），`top_k`（召回数量）
- 内部逻辑：
    1. 调用 `embed_chunk` 把用户问题转为向量
    2. 用该向量在ChromaDB中查询，取最相似的top_k个片段
    3. 返回这些片段内容列表
- **观察点**：单纯基于向量相似度的召回排序不一定准确（正确答案所在片段可能排不到第一），这是重排环节要解决的问题

---

## 六、重排 Rerank

- 使用 **CrossEncoder**（来自 sentence-transformers）
- 定义函数 `rerank(query, retrieved_chunks, top_k) -> List[str]`
- 参数：用户问题、召回的片段列表、重排后保留的数量
- 内部逻辑：
    1. 加载一个CrossEncoder模型
    2. 构造 `(query, chunk)` 配对列表，每个召回片段都和query配一对
    3. 调用CrossEncoder的预测方法，对每一对打分，分数代表query与该片段的相关程度
    4. 将片段内容与对应分数打包，按分数降序排序
    5. 取排序后的前top_k个，只保留片段内容（丢弃分数）
- **注意**：同样首次运行需下载约400MB左右的cross-encoder模型
- **效果**：重排后正确答案对应片段的排名明显优于单纯embedding检索，说明cross-encoder对相关性的判断比向量相似度更准确

---

## 七、生成 Generate

- 使用 **Gemini 2.5 Flash**（免费模型）
    
- 前置准备：
    
    1. 注册获取Gemini API Key
    2. 在项目目录新建 `.env` 文件，写入：`GEMINI_API_KEY=你的key`
    3. 用 `python-dotenv` 的 `load_dotenv()` 把`.env`中的key加载为环境变量（SDK只从环境变量读取，不会自己去读`.env`文件，`.env`只是中转）
    4. 创建一个google genai client，后续用它调用模型
- 定义函数 `generate(query, chunks) -> str`
    
- 参数：用户问题、重排后得到的片段列表
    
- 内部逻辑：
    
    1. 构造prompt（把用户问题和相关片段拼接进去）
    2. 调用Gemini模型，传入prompt
    3. 返回模型生成的答案

---

## 八、关键要点总结

1. **两阶段划分**：准备阶段（分片+索引，用户提问前完成一次）和问答阶段（召回+重排+生成，每次提问都执行）
2. **召回 ≠ 最终结果**：向量检索召回的候选集合排序未必准确，重排（cross-encoder）是提升准确率的关键一步
3. **常见依赖**：sentence-transformers（embedding + cross-encoder）、chromadb（向量库）、google-genai（生成模型调用）、python-dotenv（环境变量管理）
4. **模型下载**：embedding模型和cross-encoder模型首次使用都需联网从HuggingFace下载（各约400MB）
5. **ChromaDB版本报错**：运行中出现的报错信息多为依赖版本不兼容，不影响功能，可忽略