## 一、 技术底座与架构演进

### 1. Transformer 架构与 Decoder-Only 的确立
目前主流的生成式大模型（如 GPT-4、Claude、DeepSeek、通义千问等）均采用 Decoder-Only 架构。其底层原理是利用极强的因果掩蔽机制（Causal Masking）和上下文学习能力（In-Context Learning），基于已知上文逐字预测下一个 Token 的概率分布并进行采样生成。

### 2. Transformer 中“编码”与“解码”的四个多重层级
编码（Encoding）与解码（Decoding）出现在大模型技术的不同层级：

**网络架构层面（Model Architecture）：**
* Encoder-Only（纯编码器）：如 BERT、RoBERTa，采用双向注意力，擅长文本分类、实体识别与语义相似度计算。
* Decoder-Only（纯解码器）：如 GPT-4、LLaMA、DeepSeek，采用因果单向注意力，自回归生成文本，是生成式大模型的主流架构。
* Encoder-Decoder（编码器-解码器）：如 T5、BART 及原始 Transformer， Encoder 理解输入，Decoder 生成输出，常用于翻译与摘要。

**位置编码层面（Positional Encoding）：**
* 绝对位置编码：包含正弦/余弦固定函数位置编码（Sinusoidal，原始 Transformer 使用）和可学习位置编码（Learned Positional Embeddings，如 GPT-2）。
* 相对位置编码：包含 RoPE（旋转位置编码，通过复数旋转矩阵实现，外推性能优异，为主流大模型标配）和 ALiBi（通过注意力权重随距离增加惩罚项，具备极强长上下文外推能力）。

**符号与向量映射层面（Token Encoding & Decoding）：**
* 分词编码（Token Encoding）：通过 BPE（Byte-Pair Encoding）、WordPiece 或 Unigram 算法将文本切分为 Token 并转换为 Token ID。
* Embedding 向量化：将 Token ID 映射为高维连续向量（Embedding Vector）。

**推理生成策略层面（Inference Decoding Strategies）：**
* 确定性解码：包含贪心搜索（Greedy Search，每次选概率最高的 Token，稳定但易重复）与束搜索（Beam Search，保留概率最高的 K 个路径，常用于翻译摘要）。
* 随机采样解码：包含 Temperature（温度采样，调整分布平滑度）、Top-k 采样（在前 k 个最高概率中采样）、Top-p 核采样（累加概率达到阈值 p 的集合内采样）以及 Min-p 采样（淘汰低于最高概率乘阈值的 Token）。
* 加速解码算法：投机解码（Speculative Decoding），使用小模型（Draft Model）快速生成候选，大模型一次性并行验证，大幅提升生成速度。

## 二、 模型能力增强的三大技术路径深度对比

在业务落地中，大模型出厂的通用能力往往无法直接满足垂直场景的要求，需要通过技术手段增强：

### 1. 提示词工程
**底层原理：** 在不改变大模型参数权重的前提下，通过在输入端精心设计角色设定、上下文、思维链（Chain of Thought）或少样本示例（Few-Shot）来引导模型的输出行为。

**核心痛点与局限：**
* 受到大模型上下文窗口（Context Window）物理长度的限制。
* 提示词过长会导致首字延迟（TTFT）与 Token 消耗成本呈指数级上升。
* 面对复杂的长链路任务时容易发生上下文混淆，输出格式与确定性难以绝对控制。
* 无法把新的领域知识真正“教”给模型或补充训练期之外的新知识。

### 2. 参数微调与 LoRA 
**底层原理：** 冻结大模型原有预训练参数，在原权重矩阵旁外挂低秩分解矩阵（低秩矩阵 A 和 B），训练时仅更新低秩矩阵参数，大幅降低显存与算力开销。

**核心痛点与局限：**
* 依然需要昂贵的 GPU 算力以及高质量、经过清洗的专业场景数据集。
* 微调容易产生“灾难性遗忘”，导致模型的通用推理能力与常识明显下降。
* 属于“黑盒更新”，无法百分之百保证其不吐出有害或格式错乱信息。
* 基座模型迭代速度极快，常出现“微调迭代数月，新一代基座模型发布后原生能力直接反超”的尴尬境地。

### 3. 检索增强生成（RAG）
**底层原理：** 将企业私有文档切片（Chunking）并转换为向量（Embedding）存入向量数据库。用户提问时，系统首先在向量库中检索最相关的文档片段，将其作为背景知识拼接进 Context 增强 Prompt，再交由大模型生成带出处引用的回答。

**核心痛点与局限：**
* 无法改变模型本体推理能力，不让模型“变聪明”。
* 极度依赖前期文档解析与清洗质量，遇到多栏排版、跨页表格或扫描件极易产生垃圾输入垃圾输出（GIGO）。
* 混合检索与重排序（Reranking）配置不当易导致低相关性内容污染上下文，从而诱发模型产生严重幻觉。

## 三、 交互扩展与外部能力连接：Tool、Function Calling 与 MCP 协议

从“聊天机器人”走向“能干活的工具”，需要让模型具备操作外部系统的能力。

### 1. 三者的本质定义与核心区别
* Tool（工具）：业务概念与具体功能实体，解决“大模型能干什么”的问题。
* Function Calling（函数调用）：模型原生的结构化决策与输出能力，将自然语言意图精准转换为结构化 JSON 指令，解决“大模型如何精准表达调用意图”的问题。
* MCP（Model Context Protocol）：Anthropic 于 2024 年 11 月提出的开源协议，定义了连接模型宿主与外部工具的标准通信规范，解决“不同大模型与无数工具如何统一连接与解耦”的问题。

* ~~Tool 是打印机硬件本身，具备“打印文档”的具体物理能力。~~
* ~~Function Calling 是操作系统的打印驱动程序，将用户的打印意图翻译为打印机能识别的结构化控制指令。~~
* ~~MCP 是 USB-C 物理接口与传输协议，规定了数据怎么传输，使得任何电脑插上 USB-C 就能直接使用任何打印机。~~

### 3. 三者的协同工作流程
1. 暴露工具 (MCP Server -> Tool)：开发人员在 MCP Server 中编写工具（如 get_weather），MCP Server 通过 MCP 协议将工具名称和参数规范告知应用平台。
2. 理解与传递 (MCP Client -> Model)：应用平台（MCP Client）将获取到的工具描述塞入大模型的 Prompt 中。
3. 决策与输出 (Model -> Function Calling)：大模型接收提问后触发自身的 Function Calling 能力，输出结构化 JSON 指令（如 {"name": "get_weather", "parameters": {"city": "上海"}}）。
4. 传输与执行 (MCP Client -> MCP Server -> Tool)：应用平台通过 MCP 协议将 JSON 指令安全发送给 MCP Server，MCP Server 执行 Tool 拿到结果，再通过 MCP 协议回传给大模型汇总成回答。

### 4. 为什么有了 Function Calling 还需要 MCP
没有 MCP 之前，工具通常直接内嵌在后端代码中，导致代码高度绑定（换平台需要重写工具适配代码），且 API Key 和文件权限缺乏安全隔离。MCP 实现了系统解耦与标准化，开发者只需按照 MCP 协议编写一次工具，即可被任何支持 MCP 的 AI 客户端或 Agent 框架直接调用。

## 四、 Agent 认知架构、演进路线与设计范式

### 1. Agent 最简构成与 ReAct 智能体范式
Agent 的最简构成公式为：Agent = System Prompt + LLM + Tools。

其核心运行机制是 ReAct 范式（Reasoning and Acting，思考-行动-观察循环）：
* Thought（思考）：分析当前目标与已知信息，制定下一步计划。
* Action（行动）：选择并触发外部工具（Function Calling / MCP）。
* Observation（观察）：接收工具执行返回的结果与环境反馈。
* Loop / Finish：基于观察结果再次思考，未解决问题则继续循环，达成目标则输出最终结论。

### 2. 从学术范式到代码框架，再到可视化平台的演进
* 学术探索期（~2022 年）：学者提出思维链（CoT）、思考-行动（ReAct）、检索增强（RAG）、程序辅助语言（PAL）等纯思维范式。
* 代码框架化（2022 年底-2023 年）：LangChain、LlamaIndex、LangGraph、CrewAI 等框架将思维范式封装为成熟代码库，用代码实现 Agent Loop、PAL 沙箱运行及 Prompt 拼接。
* 可视平台化（2023 年至今）：Dify、Coze 等可视化编排平台将数据管道、LLM 路由、工具调用和分支控制封装为直观的工作流节点，大幅提升交付效率。合格的 AI 工程师需要同时具备“代码级底层重构”与“可视化画布快速交付”的双向能力。

### 3. 认知架构设计
针对大模型的物理瓶颈，通过外围工程结构提供确定性保障：
* PAL（Program-Aided Language models）：将大模型不擅长的数学计算或逻辑推演自动转换为 Python 代码，并调用本地解释器执行，把逻辑外包给代码以消除计算幻觉。
* Reflexion（自反思机制）：模型生成答案或代码后不直接输出，而是先经过单元测试或审查模型校验。若报错则将日志喂回 Prompt，触发自我重构与闭环纠偏。

### 4. Single-Agent 与 Multi-Agent 的架构权衡
* 单 Agent：架构简单、链路短、API 费用与延迟低、易于调试。但在任务极长或包含冲突职责时，容易因 Prompt 冗长而导致注意力分散甚至死循环。
* 多 Agent：适合处理上下文爆炸/污染（需子 Agent 隔离上下文）、任务可并行执行提速、以及需划分独立工具集改善决策的场景。误区：按“职能分工”（如一写一测一审）划分会导致大量的 Token 消耗在 Agent 间的互相解释上。==原则：谁掌握背景信息谁负责到底，优先优化单 Agent 的 Prompt 与工具设计。==

### 5. Agent Skill 的渐进式披露机制 (Progressive Disclosure)
为解决工具过多导致上下文爆炸和模型注意力散射的问题，Agent Skill 采用渐进式披露机制：
1. 初始化：Agent 启动时仅读取各个 Skill 的名称与简短描述，占用极少 Token。
2. 匹配激活：当用户请求与某一 Skill 匹配时，系统才动态将该 Skill 的 SKILL.md 完整指令加载进上下文。
3. 深度读取与执行：运行过程中若需具体参数或脚本，再进一步读取 reference 文件或触发沙箱执行 scripts。

## 五、 上下文工程（Context Engineering）

### 1. 上下文工程的必要性
Transformer 的自注意力机制要求每个 Token 都与其它 Token 计算相关性。过长或冗余的上下文会稀释模型的注意力，导致“中间失忆”（Lost in the Middle）、决策偏差以及巨额 Token 成本和延迟。

### 2. 上下文工程的四个操作维度
* 写（Write）：设计高密度、无二义性的 Prompt 模板，精选少量黄金 Few-Shot 样本，使用 Pydantic Schema 锁定结构化输出。
* 选（Select）：利用高精度 RAG 与元数据过滤（Metadata Filtering），仅提取与当前提问最相关的片段。
* 压（Compress）：利用摘要算法对历史对话进行提炼或剪枝（Context Pruning），剔除废话，最小化 Token 损耗。
* 隔（Isolate）：将用户输入与 System Prompt、历史对话及外部知识库进行结构隔离，防范提示词注入攻击（Prompt Injection）。

## 六、 长周期任务保障：Harness Engineering（驾驭工程）与排查体系

### 1. Harness Engineering（驾驭工程）四大要素
在长周期、无人工干预的自动化任务中，Harness Engineering 是保障 Agent 不脱轨的系统外骨骼：
* 硬性约束（Hard Constraints）：编写强规则硬代码、正则与 Pydantic 校验，锁定模型输出边界与目录权限。
* 完整上下文（Complete Context）：设计结构化 Session/State 全局状态管理器，提供完整需求文档与项目架构背景。
* 自动验证（Automated Validation）：每步关键产出配有客观自动校验机制（如代码编译测试、Pydantic 强解析）。
* 闭环纠偏（Closed-loop Error Correction）：验证不通过时将具体报错日志重写进 Prompt，触发自我修正逻辑。

### 2. 三层排查调优框架
当 AI 应用运行异常或产生幻觉时，按以下三层框架顺次排查：
* 认知层（Cognitive Layer）：排查 Prompt 描述是否存在歧义、Few-Shot 是否产生负面偏差、CoT 注意力是否偏移。
* 模式层（Pattern Layer）：排查多 Agent 状态机（State Graph）是否发生死循环、问题分类器是否分发错误、State 内存是否发生覆盖冲突。
* 系统工程外骨骼层（System/Infra Layer）：排查向量库索引召回率是否过低、Reranker 是否误杀关键文档、外部 API 是否超时（Timeout）或触及频次限制（Rate Limit）。

### 3. 终端实践项目参考
* OpenClaw：运行在本地电脑上的个人 AI 助手，支持通过飞书等日常通讯软件远程操控电脑。
* NanoBot / nanocoder：以极简代码量（约 1% 代码）实现核心上下文与记忆管理机制的精简实现标杆。

## 七、 Agent 的下一阶段：自进化（Self Evolution）架构

### 1. 传统 Agent 与自进化 Agent 的本质区别
传统 Agent 的流程为：任务 -> 规划 -> 调用工具 -> 执行 -> 结果（无经验积累，执行一万次与第一次能力无异）。
自进化 Agent 在得到结果后继续闭环：结果 -> 反馈 -> 反反思 -> 获取经验 -> 更新 -> 反哺 Agent 本身。

### 2. Reflection（反思）与 Self Evolution（自进化）的关键界限
* Reflection（反思）：解决的是“单次任务”的当次修正（如修正参数后调通接口），但下一次遇到相同问题仍需重新反思，本质上没有进化。
* Self Evolution（自进化）：解决的是“未来任务”，将改正方法永久保存（Update 环节），形成经验沉淀。

### 3. 自进化的五层架构
* Memory（记忆层）：积累经验（如发现某数据源不稳定，下次优先调用稳定数据源）。
* Policy/Prompt（策略层）：优化规划策略（如将原本 10 步流程精简为 7 步）。
* Skill（技能层）：将成功经验固化封装为可复用的技能模块（SOP）。
* Tool（工具层）：当工具不够时自主编写代码、调试并验证，封装为新工具加入工具库（从选工具进化到造工具）。
* Model（模型层）：利用真实环境中的轨迹数据构建训练集进行 SFT 或 RL，更新模型参数本身。

### 4. 经验飞轮 (Experience Flywheel) 与新评估标准
自进化 Agent 形成“执行 -> 反馈 -> 反思 -> 经验 -> 更新 -> 更强表现”的经验飞轮。未来评估 Agent 的标准不在于单次表现，而在于其执行 1000 次任务后是否比第一次更强。AI 工程师的角色也将全面转变为系统架构师与驾驭者（Harnesser）。